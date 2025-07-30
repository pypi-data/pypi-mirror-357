from dataclasses import dataclass
from typing import NamedTuple

from psycopg import Column
from psycopg.pq import ExecStatus
from psycopg.rows import TupleRow


@dataclass
class Result:
    query: str
    exec_status: ExecStatus
    command_status: str | None
    num_rows: int | None
    duration: float
    notices: list[str]


@dataclass
class DataResult(Result):
    rows: list[TupleRow]
    columns: list[Column]


@dataclass
class ErrorResult(Result):
    error: str


class ResultSet(NamedTuple):
    results: list[Result]
    duration: float


@dataclass
class DbInfo:
    """Database info loaded from the server"""

    database: str
    host: str
    host_address: str
    port: str
    schema: str
    user: str


@dataclass
class DbContext:
    """Credentials used to connect to the database"""

    dbname: str | None
    host: str
    password: str | None
    port: str
    username: str
