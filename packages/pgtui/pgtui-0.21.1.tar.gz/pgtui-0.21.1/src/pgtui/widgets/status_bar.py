from rich.console import RenderableType
from textual.timer import Timer
from textual.widgets import Label


class StatusBar(Label):
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        dock: bottom;
    }
    """

    def __init__(self, initial: RenderableType = ""):
        self.timer: Timer | None = None
        super().__init__(initial)

    # TODO: support multiple messages
    def set_message(self, text: str, timeout: float | None = None):
        if self.timer:
            self.timer.stop()

        self.update(text)

        if timeout:
            self.timer = self.set_timer(timeout, callback=self.clear)

    def clear(self):
        self.update()
