import re
from pathlib import Path

from psycopg import AsyncConnection
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Input, Label, RadioButton, RadioSet

from pgtui.db import ExportFormat, export_csv, export_json, export_text
from pgtui.utils.datetime import format_duration
from pgtui.widgets.dialog import ConfirmationDialog
from pgtui.widgets.modal import ModalScreen, ModalTitle
from pgtui.widgets.status_bar import StatusBar

EXTENSIONS = {
    ExportFormat.CSV: ".csv",
    ExportFormat.JSON: ".json",
    ExportFormat.TEXT: ".txt",
}


class ExportDialog(ModalScreen[str]):
    DEFAULT_CSS = """
    .dialog_text {
        margin-top: 1;
        margin-left: 1;
    }
    .format_label {
        margin-left: 1;
    }
    .action_container {
        layout: grid;
        grid-columns: 1fr auto auto;
        grid-size: 3;
        height: auto;
        margin-top: 1;
        Button {
            margin-left: 1;
            margin-top: 2;
        }
        Vertical {
            height: auto;
        }
    }
    """

    def __init__(self, conn: AsyncConnection, query: str):
        super().__init__()
        self.conn = conn
        self.export_query = query
        self.format = ExportFormat.JSON

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle("Export query")
        yield Label("Export to:", classes="dialog_text")
        yield Input(value="export.json")
        with Container(classes="action_container"):
            with Vertical():
                yield Label("Format:", classes="format_label")
                with RadioSet():
                    yield RadioButton("JSON", value=True, id=ExportFormat.JSON)
                    yield RadioButton("CSV", id=ExportFormat.CSV)
                    yield RadioButton("TEXT", id=ExportFormat.TEXT)
            yield Button("Export", id="ex_export_btn", variant="primary")
            yield Button("Cancel", id="ex_cancel_btn")
        yield StatusBar()

    def show_status(self, message: str):
        self.query_one(StatusBar).set_message(message)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ex_export_btn":
            self.export()

        if event.button.id == "ex_cancel_btn":
            self.dismiss()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.format = ExportFormat(event.pressed.id)
        self._switch_extension(self.format)

    def _switch_extension(self, format: ExportFormat):
        input = self.query_one(Input)
        target_ext = EXTENSIONS[format]
        for ext in EXTENSIONS.values():
            if ext != target_ext:
                input.value = re.sub(rf"{ext}$", target_ext, input.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.export()

    @work
    async def export(self):
        path = await self._get_path()
        if not path:
            return

        try:
            result = await self._export_to_format(path)
            msg = f"Exported {result.row_count} rows to '{result.path}' in {format_duration(result.duration)}"
            self.dismiss(f"[green]{msg}[/green]")
        except Exception as ex:
            self.dismiss(f"[red]Export failed: {str(ex)}[/]")

    async def _export_to_format(self, path: Path):
        match self.format:
            case ExportFormat.JSON:
                return await export_json(self.conn, self.export_query, path)
            case ExportFormat.CSV:
                return await export_csv(self.conn, self.export_query, path)
            case ExportFormat.TEXT:
                return await export_text(self.conn, self.export_query, path)

    async def _get_path(self) -> Path | None:
        str_path = self.query_one(Input).value.strip()
        if not str_path.strip():
            self.show_status("[red]No path given[/]")
            return

        path = Path(str_path)
        if path.exists():
            if path.is_dir():
                self.show_status("[red]Given path is an existing directory.[/red]")
                return

            overwrite = await self.app.push_screen_wait(
                ConfirmationDialog(
                    title="Overwrite file?",
                    text=f"{path} already exists. Overwrite?",
                )
            )

            if not overwrite:
                return

        return path
