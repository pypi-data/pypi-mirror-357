from pathlib import Path

from textual import on, work
from textual.app import App
from textual.widgets import Header, TabbedContent, TabPane
from textual_fspicker import FileOpen

from pgtui import __version__
from pgtui.bindings import bindings
from pgtui.entities import DbContext
from pgtui.messages import ShowException
from pgtui.utils import sql_filters
from pgtui.widgets.dialog import ErrorDialog, HelpDialog
from pgtui.widgets.pane import EditorPane
from pgtui.widgets.tabbed_content import SwitchingTabbedContent
from pgtui.widgets.text_area import SqlTextArea


class PgTuiApp(App[None]):
    TITLE = "pgtui"
    SUB_TITLE = __version__
    CSS_PATH = "app.css"

    BINDINGS = [
        bindings.exit.bind("exit"),
        bindings.show_help.bind("show_help"),
        bindings.new_tab.bind("add_pane"),
        bindings.open_file.bind("open_file"),
        ("ctrl+print_screen", "take_screenshot"),
    ]

    def __init__(self, ctx: DbContext, file_path: Path | None):
        super().__init__()
        self.ctx = ctx
        self.file_path = file_path
        self.animation_level = "none"
        self.tc = SwitchingTabbedContent(id="editor_tabbed_content")

    def compose(self):
        yield Header()
        yield self.tc

    async def on_mount(self):
        await self.add_pane(self.file_path)

    def on_show_exception(self, message: ShowException):
        self.push_screen(ErrorDialog("Error", str(message.exception)))

    @on(EditorPane.Close)
    def on_pane_close(self, event: EditorPane.Close):
        if event.tab_pane.id is not None:
            self.tc.remove_pane(event.tab_pane.id)

    @on(EditorPane.Dirty)
    def on_pane_dirty(self, event: EditorPane.Dirty):
        label = event.file_path.name if event.file_path else "untitled"
        self.tc.get_tab(event.tab_pane).label = f"{label}*"

    @on(EditorPane.Saved)
    def on_pane_saved(self, event: EditorPane.Saved):
        self.tc.get_tab(event.tab_pane).label = event.file_path.name

    async def add_pane(self, file_path: Path | None = None):
        pane = EditorPane(self.ctx, file_path)
        await self.tc.add_pane(pane)
        self.activate_pane(pane)

    def activate_pane(self, pane: TabPane):
        assert pane.id is not None
        self.tc.active = pane.id

    @on(TabbedContent.TabActivated)
    def _on_tab_activated(self, event: TabbedContent.TabActivated):
        if event.tabbed_content.id == "editor_tabbed_content":
            self._focus_text_area(event.pane)

    # Make this exclusive so future events will cancel any pending ones.
    # This speeds up skipping over tabs.
    @work(group="_focus_text_area", exclusive=True)
    async def _focus_text_area(self, pane: TabPane):
        pane.query_one(SqlTextArea).focus()

    def action_show_help(self):
        self.app.push_screen(HelpDialog())

    async def action_add_pane(self):
        await self.add_pane()

    @work
    async def action_open_file(self):
        dialog = FileOpen(filters=sql_filters())
        path = await self.push_screen_wait(dialog)
        if path:
            await self.add_pane(path)

    @work
    async def action_exit(self):
        for pane in self.query(EditorPane):
            should_close = await pane.save_before_close()
            if should_close:
                assert pane.id
                self.tc.remove_pane(pane.id)
            else:
                return

        self.app.exit()

    def action_take_screenshot(self):
        path = self.save_screenshot()
        self.notify(f"Saved {path}")
