import logging
import time
from contextlib import asynccontextmanager
from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Callable, NamedTuple

import sqlparse
from psycopg import AsyncConnection, AsyncCursor
from psycopg.conninfo import make_conninfo
from psycopg.errors import DatabaseError, Diagnostic
from psycopg.pq import ExecStatus
from psycopg.rows import AsyncRowFactory, TupleRow

from pgtui.entities import DataResult, DbContext, DbInfo, ErrorResult, Result, ResultSet
from pgtui.utils.datetime import format_duration

logger = logging.getLogger(__name__)


MAX_FETCH_ROWS = 200
"""
Max rows to fetch at once to avoid loading a very large table into DataTable
accidentally.
TODO: make configurable
"""


async def fetch_db_info(conn: AsyncConnection) -> DbInfo:
    query = """
    SELECT current_database() AS database,
           current_user AS user,
           current_schema AS schema;
    """

    cursor = await conn.execute(query)
    row = await cursor.fetchone()
    assert row is not None
    database, user, schema = row

    return DbInfo(
        host=conn.pgconn.host.decode(),
        host_address=conn.pgconn.hostaddr.decode(),
        port=conn.pgconn.port.decode(),
        database=database,
        schema=schema,
        user=user,
    )


async def fetch_databases(conn: AsyncConnection) -> list[str]:
    query = """
    SELECT datname
    FROM pg_database
    WHERE datallowconn AND NOT datistemplate;
    """

    rows = await select(conn, query)
    return [r[0] for r in rows]


async def select(conn: AsyncConnection, query: str) -> list[TupleRow]:
    async with execute(conn, query) as cursor:
        return await cursor.fetchall()


async def run_queries(conn: AsyncConnection, queries: str) -> ResultSet:
    results: list[Result] = []
    start = time.monotonic()

    for query in sqlparse.split(queries):
        notices: list[str] = []
        query_start = time.monotonic()

        def handle_notice(diag: Diagnostic):
            log_diagnostic(diag)
            if diag.message_primary:
                notices.append(f"{diag.severity}: {diag.message_primary}")
            if diag.message_detail:
                notices.append(f"{diag.severity}: {diag.message_detail}")
            if diag.message_hint:
                notices.append(f"{diag.severity}: {diag.message_hint}")

        try:
            logger.info("Adding notice handler")
            conn.add_notice_handler(handle_notice)
            async with execute(conn, query) as cursor:
                result = await _cursor_result(cursor, query, query_start, notices)
                results.append(result)
        except DatabaseError as ex:
            log_diagnostic(ex.diag)
            results.append(_ex_result(ex, query, query_start, notices))
            break  # Stop running queries on error
        finally:
            logger.info("Removing notice handler")
            conn.remove_notice_handler(handle_notice)

    duration = time.monotonic() - start
    return ResultSet(results, duration)


def log_diagnostic(diag: Diagnostic):
    # TODO: probably overkill but useful for now
    logger.debug(f"""Diagnostic:
    {diag.severity=}
    {diag.severity_nonlocalized=}
    {diag.sqlstate=}
    {diag.message_primary=}
    {diag.message_detail=}
    {diag.message_hint=}
    {diag.statement_position=}
    {diag.internal_position=}
    {diag.internal_query=}
    {diag.context=}
    {diag.schema_name=}
    {diag.table_name=}
    {diag.column_name=}
    {diag.datatype_name=}
    {diag.constraint_name=}
    {diag.source_file=}
    {diag.source_line=}
    {diag.source_function=}""")


async def _cursor_result(
    cursor: AsyncCursor[TupleRow],
    query: str,
    start: float,
    notices: list[str],
):
    assert cursor.pgresult is not None
    exec_status = ExecStatus(cursor.pgresult.status)
    duration = time.monotonic() - start

    # rowcount will be -1 for queries which don't affect rows
    num_rows = cursor.rowcount if cursor.rowcount >= 0 else None

    if exec_status == ExecStatus.TUPLES_OK:
        rows = await _fetch(cursor) if cursor.rowcount > 0 else []
        columns = cursor.description
        assert columns is not None

        return DataResult(
            query=query,
            rows=rows,
            columns=columns,
            num_rows=num_rows,
            duration=duration,
            command_status=cursor.statusmessage,
            notices=notices,
            exec_status=exec_status,
        )
    else:
        return Result(
            query=query,
            num_rows=num_rows,
            duration=duration,
            command_status=cursor.statusmessage,
            notices=notices,
            exec_status=exec_status,
        )


def _ex_result(
    ex: DatabaseError,
    query: str,
    start: float,
    notices: list[str],
):
    duration = time.monotonic() - start
    assert ex.pgresult is not None
    exec_status = ExecStatus(ex.pgresult.status)

    # TODO: can error contain diag.message_detail or diag.message_hint?

    return ErrorResult(
        error=str(ex),
        query=query,
        num_rows=None,
        duration=duration,
        command_status="[red]ERROR[/red]",
        notices=notices,
        exec_status=exec_status,
    )


async def _fetch(cursor: AsyncCursor) -> list[TupleRow]:
    start = time.monotonic()
    logger.info(f"Fetching {MAX_FETCH_ROWS}/{cursor.rowcount} rows")
    rows = await cursor.fetchmany(MAX_FETCH_ROWS)
    duration = time.monotonic() - start
    logger.info(f"Fetched {len(rows)} rows in {format_duration(duration)}")
    return rows


@asynccontextmanager
async def execute(conn: AsyncConnection, query: str):
    logger.info(f"Running query: {query}")
    async with conn.cursor() as cursor:
        await cursor.execute(query.encode())
        yield cursor


class ExportResult(NamedTuple):
    path: Path
    row_count: int
    duration: float


class ExportFormat(StrEnum):
    JSON = auto()
    CSV = auto()
    TEXT = auto()


ProgressCallback = Callable[[int, int], Any]


async def export_json(
    conn: AsyncConnection,
    query: str,
    target: Path,
    progress_callback: ProgressCallback | None = None,
) -> ExportResult:
    logger.info(f"Exporting query: {query}")
    start = time.monotonic()
    async with conn.cursor() as cursor:
        query = query.strip().strip(";")
        export_query = f"SELECT row_to_json(data)::TEXT FROM ({query}) AS data"
        await cursor.execute(export_query.encode())

        row_no = 1
        with open(target, "w") as f:
            f.write("[")
            async for row in cursor:
                if row_no > 1:
                    f.write(",")
                f.write(row[0])
                if progress_callback:
                    progress_callback(row_no, cursor.rowcount)
                row_no += 1
            f.write("]")

        duration = time.monotonic() - start
        return ExportResult(target, cursor.rowcount, duration)


async def export_csv(conn: AsyncConnection, query: str, target: Path) -> ExportResult:
    return await _export_copy(conn, query, target, "CSV HEADER")


async def export_text(conn: AsyncConnection, query: str, target: Path) -> ExportResult:
    return await _export_copy(conn, query, target, "HEADER")


async def _export_copy(
    conn: AsyncConnection,
    query: str,
    target: Path,
    options: str,
) -> ExportResult:
    start = time.monotonic()
    async with conn.cursor() as cursor:
        query = query.strip().strip(";")
        export_query = f"COPY({query}) TO STDOUT {options};"

        async with cursor.copy(export_query.encode()) as copy:
            with open(target, "wb") as f:
                while block := await copy.read():
                    f.write(block)

        duration = time.monotonic() - start
        return ExportResult(target, cursor.rowcount, duration)


async def make_connection(
    ctx: DbContext,
    *,
    row_factory: AsyncRowFactory | None = None,
    autocommit: bool = True,
) -> AsyncConnection:
    conninfo = make_conninfo(
        user=ctx.username,
        password=ctx.password,
        dbname=ctx.dbname,
        host=ctx.host,
        port=ctx.port,
    )

    return await AsyncConnection.connect(
        conninfo,
        row_factory=row_factory,
        autocommit=autocommit,
    )
