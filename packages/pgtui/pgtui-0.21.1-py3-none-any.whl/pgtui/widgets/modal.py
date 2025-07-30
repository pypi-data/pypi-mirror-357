from rich.console import RenderableType
from textual import screen
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Label


class ModalScreen(screen.ModalScreen[screen.ScreenResultType]):
    DEFAULT_CSS = """
    .modal_container {
        align: center middle;
    }

    .modal_content {
        max-width: 80;
        height: auto;
        border: round gray;
    }
    """

    BINDINGS = [
        Binding("q,escape", "quit", "Close"),
    ]

    def compose_modal(self) -> ComposeResult:
        raise NotImplementedError()

    def compose(self) -> ComposeResult:
        with Container(classes="modal_container"):
            with Container(classes="modal_content"):
                yield from self.compose_modal()

    def action_quit(self):
        self.dismiss()


class ModalTitle(Label):
    DEFAULT_CSS = """
    ModalTitle {
        width: 100%;
        text-align: center;
        background: $secondary;
        dock: top;

        &.error {
            background: $error;
        }
    }
    """

    def __init__(self, renderable: RenderableType, error: bool = False):
        super().__init__(renderable, markup=False, classes="error" if error else "")
