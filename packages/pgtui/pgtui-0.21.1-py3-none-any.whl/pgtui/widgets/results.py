from datetime import datetime
from itertools import cycle
import re
from typing import Any, Iterable

from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from rich.text import Text
from textual import on, work
from textual.containers import Container, VerticalScroll
from textual.widget import Widget
from textual.widgets import DataTable, Label, TabbedContent, TabPane
from textual.widgets.data_table import CursorType

from pgtui.bindings import bindings
from pgtui.entities import DataResult, ErrorResult, Result, ResultSet
from pgtui.utils.datetime import format_duration
from pgtui.widgets.export import ExportDialog
from pgtui.widgets.status_bar import StatusBar
from pgtui.widgets.tabbed_content import SwitchingTabbedContent


class Results(Widget):
    DEFAULT_CSS = """
    Results:focus-within {
        background: $boost;
    }

    TabPane {
        padding: 0;
    }
    """

    def __init__(self, result_set: ResultSet, conn: AsyncConnection):
        super().__init__()
        self.result_set = result_set
        self.conn = conn

    def compose(self):
        results = self.result_set.results

        if not results:
            yield Label("No data")
            return

        elif len(results) == 1:
            yield ResultWidget(results[0], self.conn)
        else:
            with SwitchingTabbedContent(id="results_tabbed_content"):
                for result in results:
                    title = result.command_status or "???"
                    with TabPane(title):
                        yield ResultWidget(result, self.conn)

    @on(TabbedContent.TabActivated)
    def _on_tab_activated(self, event: TabbedContent.TabActivated):
        if event.tabbed_content.id == "results_tabbed_content":
            self._focus_result()

    # Make this exclusive so future events will cancel any pending ones.
    # This speeds up skipping over tabs.
    @work(group="_focus_result", exclusive=True)
    async def _focus_result(self):
        tc = self.query_one(SwitchingTabbedContent)
        assert tc.active_pane is not None
        tc.active_pane.query_one(ResultWidget).focus_result()


class ResultWidget(Widget):
    BINDINGS = [
        bindings.export.bind("export"),
    ]

    DEFAULT_CSS = """
    ResultWidget {
        height: auto;
    }
    """

    def __init__(self, result: Result, conn: AsyncConnection):
        super().__init__()
        self.result = result
        self.conn = conn

    def compose(self):
        with Container():  # without this scroll is broken
            if isinstance(self.result, DataResult):
                yield ResultsTable(self.result)
                yield StatusBar(self._format_status(self.result))
            else:
                yield ResultInfo(self.result)

    def focus_result(self):
        # It's one or the other
        self.query(ResultsTable).focus()
        self.query(ResultInfo).focus()

    @work
    async def action_export(self):
        if isinstance(self.result, DataResult):
            dialog = ExportDialog(self.conn, self.result.query)
            message = await self.app.push_screen_wait(dialog)
            if message:
                self.query_one(StatusBar).set_message(message)

    def _format_status(self, result: DataResult):
        duration = format_duration(result.duration)
        fetched = len(result.rows)
        total = result.num_rows

        if fetched != total:
            return f"Fetched {fetched}/{total} rows in {duration}"
        else:
            return f"Fetched {total} rows in {duration}"


class ResultInfo(VerticalScroll):
    DEFAULT_CSS = """
    ResultInfo {
        padding: 1;
        .title { text-style: bold }
        .query { text-style: dim }
    }
    """

    def __init__(self, result: Result):
        super().__init__()
        self.result = result

    def compose(self):
        query = re.sub(r"\s+", " ", self.result.query)

        yield Label(f"{datetime.now()}", classes="title")
        yield Label(f"Query: {query}", classes="query")
        yield Label(f"Status: {self.result.exec_status.name}")
        if self.result.num_rows is not None:
            yield Label(f"Affected rows: {self.result.num_rows}")
        yield Label(f"Time: {format_duration(self.result.duration)}")
        for notice in self.result.notices:
            yield Label(notice, classes="warning")
        if isinstance(self.result, ErrorResult):
            yield Label(f"ERROR: {self.result.error}", classes="error")


class ResultsTable(DataTable[Any]):
    BINDINGS = [
        bindings.toggle_cursor.bind("toggle_cursor"),
    ]

    def __init__(self, result: DataResult):
        super().__init__()
        self.result = result

        self.cursors: Iterable[CursorType] = cycle(["cell", "row", "column", "none"])
        self.cursor_type = next(self.cursors)

        self.add_columns(*[c.name for c in result.columns])
        self.add_rows(mark_nulls(result.rows))

    def action_toggle_cursor(self):
        self.cursor_type = next(self.cursors)


NULL = Text("<null>", "dim")


def mark_nulls(rows: Iterable[TupleRow]) -> Iterable[TupleRow]:
    """Replaces nulls in db data with a styled <null> marker."""
    return (tuple(cell if cell is not None else NULL for cell in row) for row in rows)
