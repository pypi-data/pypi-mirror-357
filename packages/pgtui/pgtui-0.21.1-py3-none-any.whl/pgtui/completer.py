"""
Completion is fully yanked from pgcli ^^;
"""

import logging
import time

from pgcli.completion_refresher import CompletionRefresher
from pgcli.pgcompleter import Completion, PGCompleter
from pgcli.pgexecute import PGExecute
from prompt_toolkit.document import Document

from pgtui.entities import DbContext
from pgtui.utils.datetime import format_duration

logger = logging.getLogger(__name__)


class QueryCompleter:
    @classmethod
    def from_context(cls, ctx: DbContext):
        return cls(
            database=ctx.dbname,
            user=ctx.username,
            password=ctx.password,
            host=ctx.host,
            port=ctx.port,
        )

    def __init__(
        self,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: str | None = None,
    ):
        self.completer: PGCompleter | None = None
        self.executor = PGExecute(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        self.refresher = CompletionRefresher()

        logger.info("Refreshing started")
        self.refresher.refresh(
            self.executor,
            special=None,
            callbacks=lambda c: self.set_completer(c),
        )

    def set_completer(self, completer: PGCompleter):
        logger.info("Refreshing ended")
        self.completer = completer
        self.completer.set_search_path(self.executor.search_path())

    def get_completions(self, sql: str, cursor_position: int) -> list[Completion]:
        if not self.completer:
            return []

        start = time.monotonic()
        document = Document(sql, cursor_position)
        completions = self._get_completions(document)
        duration = format_duration(time.monotonic() - start)
        logger.debug(f"Loaded {len(completions)} completions in {duration}")
        return completions

    def _get_completions(self, document: Document) -> list[Completion]:
        return self.completer.get_completions(document, None)
