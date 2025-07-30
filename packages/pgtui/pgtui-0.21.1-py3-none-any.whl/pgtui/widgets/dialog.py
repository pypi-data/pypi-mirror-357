from itertools import groupby

from textual import on
from textual.app import ComposeResult
from textual.widgets import Button, Input, Label, Static

from pgtui import __version__
from pgtui.bindings import Binding, bindings
from pgtui.widgets.menu import Menu, MenuItem
from pgtui.widgets.modal import ModalScreen, ModalTitle


class MessageDialog(ModalScreen[None]):
    DEFAULT_CSS = """
    .dialog_button {
        height: 1;
        min-width: 1;
        border: none;
        border-top: none;
        border-bottom: none;
    }
    """

    def __init__(self, title: str, body: str | None, error: bool = False):
        self.message_title = title
        self.message_body = body
        self.error = error
        super().__init__()

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(self.message_title, error=self.error)
        if self.message_body:
            yield Static(self.message_body, markup=False)
        yield Button("[ OK ]", variant="default", classes="dialog_button")

    def on_button_pressed(self, message: Button.Pressed):
        self.dismiss()


class ErrorDialog(MessageDialog):
    def __init__(self, title: str, body: str | None):
        super().__init__(title=title, body=body, error=True)


class ConfirmationDialog(ModalScreen[bool]):
    def __init__(
        self,
        title: str,
        *,
        text: str | None = None,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
    ):
        self.modal_title = title
        self.modal_text = text
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        super().__init__()

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(self.modal_title)
        if self.modal_text:
            yield Label(self.modal_text)
        with Menu():
            yield MenuItem("confirm", self.confirm_label)
            yield MenuItem("cancel", self.cancel_label)

    @on(Menu.ItemSelected)
    def _on_item_selected(self, message: Menu.ItemSelected):
        message.stop()
        self.dismiss(message.item.code == "confirm")


class ChoiceDialog(ModalScreen[str]):
    def __init__(
        self,
        title: str,
        choices: list[tuple[str, str]],
    ):
        self.modal_title = title
        self.choices = choices
        super().__init__()

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(self.modal_title)
        with Menu():
            for code, label in self.choices:
                yield MenuItem(code, label)

    @on(Menu.ItemSelected)
    def _on_selected(self, message: Menu.ItemSelected):
        message.stop()
        self.dismiss(message.item.code)


class TextPromptDialog(ModalScreen[str]):
    DEFAULT_CSS = """
    .dialog_text {
        margin-left: 1;
    }

    Input {
        outline: heavy $background;
    }

    Input:focus {
        outline: heavy $secondary;
    }
    """

    def __init__(
        self,
        title: str,
        *,
        text: str | None = None,
        initial_value: str | None = None,
        placeholder: str = "",
    ):
        super().__init__()
        self.dialog_title = title
        self.dialog_text = text
        self.initial_value = initial_value
        self.placeholder = placeholder

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(self.dialog_title)
        if self.dialog_text:
            yield Label(self.dialog_text, classes="dialog_text")
        yield Input(self.initial_value, placeholder=self.placeholder)

    @on(Input.Submitted)
    def on_submitted(self):
        self.dismiss(self.query_one(Input).value)


class HelpDialog(ModalScreen[str]):
    DEFAULT_CSS = """
    VerticalScroll {
        height: auto;
        padding: 0 1;
        max-height: 80vh;
    }

    .group {
        width: 100%;
        margin: 1 0;
        background: $primary;
        content-align-horizontal: center;
    }
    """

    def compose_modal(self) -> ComposeResult:
        all_bindings = list(bindings.all())
        key_w, desc_w = self._calc_widths(all_bindings)

        yield ModalTitle(f"pgtui {__version__}")
        for group, group_bindings in groupby(all_bindings, lambda b: b.group):
            yield Label(group, classes="group")
            for binding in group_bindings:
                yield Label(f"{binding.key.rjust(key_w)} - {binding.description.ljust(desc_w)}")

    def _calc_widths(self, bindings: list[Binding]):
        max_key_width = max(len(b.key) for b in bindings)
        max_desc_width = max(len(b.description) for b in bindings)
        return max_key_width, max_desc_width
