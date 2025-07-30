import logging
from asyncio import Lock
from dataclasses import dataclass
from pathlib import Path

from pgcli.pgcompleter import Completion  # type: ignore
from psycopg import Error
from psycopg.pq import TransactionStatus
from textual import on, work
from textual.containers import Container
from textual.document._syntax_aware_document import SyntaxAwareDocument
from textual.geometry import Offset
from textual.widgets import TabPane, TextArea
from textual_fspicker import FileSave

from pgtui.bindings import bindings
from pgtui.completer import QueryCompleter
from pgtui.db import ResultSet, fetch_databases, fetch_db_info, make_connection, run_queries
from pgtui.entities import DbContext
from pgtui.messages import RunQuery, ShowException
from pgtui.utils import random_id, sql_filters
from pgtui.widgets.autocomplete import AutocompleteMenu
from pgtui.widgets.containers import SwitchingLayout
from pgtui.widgets.dialog import (
    ChoiceDialog,
    ConfirmationDialog,
    ErrorDialog,
)
from pgtui.widgets.footer import DbFooter
from pgtui.widgets.results import Results
from pgtui.widgets.text_area import Autocomplete, SqlTextArea

logger = logging.getLogger(__name__)


class EditorPane(TabPane):
    BINDINGS = [
        bindings.select_database.bind("select_database"),
        bindings.switch_layout.bind("switch_layout"),
        bindings.save.bind("save"),
        bindings.close_tab.bind("close"),
    ]

    DEFAULT_CSS = """
    EditorPane {
        padding: 0;
        layers: below above;

        SwitchingLayout, DbFooter {
            layer: below;
        }

        AutocompleteMenu {
            layer: above;
        }

        .results {
            border-top: solid gray;
        }

        .results:focus-within {
            background: $boost;
        }
    }
    """

    @dataclass
    class Close(TabPane.TabPaneMessage): ...

    @dataclass
    class Saved(TabPane.TabPaneMessage):
        file_path: Path

    @dataclass
    class Dirty(TabPane.TabPaneMessage):
        file_path: Path | None

    def __init__(self, ctx: DbContext, file_path: Path | None):
        self.ctx = ctx
        self.file_path = file_path
        self.exec_lock = Lock()
        self.dirty = False
        self.completer: QueryCompleter | None = None

        title = file_path.name if file_path else "[dim]untitled[/]"

        super().__init__(
            title,
            SwitchingLayout(
                SqlTextArea(self._get_initial_text()),
                Container(classes="results"),
            ),
            DbFooter(),
            AutocompleteMenu(),
            id=random_id(),
        )

    def _get_initial_text(self) -> str:
        if self.file_path and self.file_path.exists():
            logger.info(f"Loading initial text from {self.file_path}")
            with open(self.file_path) as f:
                return f.read()
        return ""

    def on_mount(self):
        self.call_after_refresh(self.connect)

    @work
    async def connect(self):
        self.completer = QueryCompleter.from_context(self.ctx)
        self.conn = await make_connection(self.ctx)

        footer = self.query_one(DbFooter)
        footer.tx_status = self.transaction_status
        footer.db_info = await fetch_db_info(self.conn)

    @work
    async def run_query(self, query: str):
        if self.exec_lock.locked():
            self.app.notify("Another query is running")
            return

        try:
            self.query_one(DbFooter).running_query = True
            async with self.exec_lock:
                result_set = await run_queries(self.conn, query)
                await self.show_results(result_set)
        except Error as ex:
            # Unexpected exception, run_queries handles DatabaseError
            logger.error(f"Query failed: {ex}")
            self.post_message(ShowException(ex))
        finally:
            with self.app.batch_update():
                footer = self.query_one(DbFooter)
                footer.tx_status = self.transaction_status
                footer.running_query = False

    async def on_run_query(self, message: RunQuery):
        self.last_query = None
        self.run_query(message.query)

    async def show_results(self, result_set: ResultSet):
        container = self.query_one(".results", Container)
        async with container.batch():
            await container.remove_children()
            await container.mount(Results(result_set, self.conn))

    @on(TextArea.Changed)
    def on_changed(self, _):
        if not self.dirty:
            self.dirty = True
            self.post_message(self.Dirty(self, self.file_path))

    def action_switch_layout(self):
        self.query_one(SwitchingLayout).switch()

    @work
    async def action_select_database(self):
        databases = await fetch_databases(self.conn)
        choices = [(db, db) for db in databases]
        dialog = ChoiceDialog("Select database", choices)
        dbname = await self.app.push_screen_wait(dialog)
        if dbname:
            self.ctx.dbname = dbname
            self.connect()

    @work
    async def action_save(self):
        path = self.file_path or await self._get_save_file_path()
        if path:
            self._save(path)

    @work
    async def action_close(self):
        await self.close()

    async def close(self):
        should_close = await self.save_before_close()
        if should_close:
            self.post_message(self.Close(self))

    async def save_before_close(self) -> bool:
        """
        Prompt the user to save changes if required.

        Returns a boolean indicating whether the dialog should be closed
        afterwards.
        """
        if not self.dirty:
            return True

        match await self._prompt_save_on_close():
            case "save":
                path = self.file_path or await self._get_save_file_path()
                if path:
                    self._save(path)
                    return True
            case "close":
                return True
            case _:
                pass

        return False

    def _save(self, file_path: Path):
        try:
            with open(file_path, "w") as f:
                contents = self.query_one(SqlTextArea).text
                f.write(contents)
        except Exception as ex:
            self.app.push_screen(ErrorDialog("Failed saving file", str(ex)))

        self.dirty = False
        self.file_path = file_path
        self.post_message(self.Saved(self, file_path))

    async def _get_save_file_path(self) -> Path | None:
        dialog = FileSave(filters=sql_filters())
        path = await self.app.push_screen_wait(dialog)
        if not path:
            return

        if path.is_dir():
            self.app.push_screen(ErrorDialog("Invalid path", "Given path is a directory"))
            return

        if path.exists() and not await self._confirm_overwrite(path):
            return

        return path

    async def _confirm_overwrite(self, path: Path) -> bool:
        dialog = ConfirmationDialog("Overwrite?", text=f"File '{path}' exists, overwrite?")
        return await self.app.push_screen_wait(dialog)

    async def _prompt_save_on_close(self):
        return await self.app.push_screen_wait(
            ChoiceDialog(
                title="Save changes before closing?",
                choices=[
                    ("save", "Save"),
                    ("close", "Close without saving"),
                    ("cancel", "Cancel"),
                ],
            )
        )

    # Handle autocomplete events

    @on(Autocomplete.Open)
    def on_open(self, _):
        self.autocomplete_update()
        self.autocomplete_move_to_cursor()
        self.autocomplete_open()

    @on(Autocomplete.Close)
    def on_close(self, _):
        self.autocomplete_close()

    @on(Autocomplete.Update)
    def on_update(self, _):
        self.autocomplete_move_to_cursor()
        self.autocomplete_update()

    @on(Autocomplete.Up)
    def on_up(self, _):
        self.autocomplete.move_up()

    @on(Autocomplete.Down)
    def on_down(self, _):
        self.autocomplete.move_down()

    @on(Autocomplete.PageUp)
    def on_page_up(self, _):
        self.autocomplete.page_up()

    @on(Autocomplete.PageDown)
    def on_page_down(self, _):
        self.autocomplete.page_down()

    @on(Autocomplete.Apply)
    def on_apply(self, _):
        if completion := self.autocomplete.selected_completion:
            self.text_area.apply_completion(completion)

        self.autocomplete_close()

    def get_completions(self) -> list[Completion]:
        """Returns the completions at current cursor position"""
        if not self.completer:
            return []
        text = self.text_area.text
        document = self.text_area.document
        assert isinstance(document, SyntaxAwareDocument)
        index = document.get_index_from_location(self.text_area.cursor_location)
        return self.completer.get_completions(text, index)

    def autocomplete_update(self):
        completions = self.get_completions()
        if completions:
            self.autocomplete.update(completions)
        else:
            self.autocomplete_close()

    def autocomplete_open(self):
        self.text_area.is_autocomplete_open = True
        self.autocomplete.display = True

    def autocomplete_move_to_cursor(self):
        self.autocomplete.offset = self._autcomplete_offset()

    def autocomplete_close(self):
        self.text_area.is_autocomplete_open = False
        self.autocomplete.display = False

    def _autcomplete_offset(self) -> Offset:
        cursor_offset = self.text_area.cursor_screen_offset
        text_area_offset = self.text_area.region.offset
        offset = cursor_offset - text_area_offset + Offset(0, 1)

        # Make sure it doesn't go off the right edge of screen
        right = offset.x + self.autocomplete.width
        max_right = self.app.screen.region.right
        if right > max_right:
            return offset - Offset(right - max_right, 0)

        # TODO: check for bottom screen edge too

        return offset

    @property
    def autocomplete(self):
        return self.query_one(AutocompleteMenu)

    @property
    def text_area(self):
        return self.query_one(SqlTextArea)

    @property
    def transaction_status(self) -> TransactionStatus:
        return TransactionStatus(self.conn.pgconn.transaction_status)
