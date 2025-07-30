from dataclasses import dataclass, fields

from textual.binding import Binding as TextualBinding

from pgtui.config import load_settings


@dataclass(frozen=True)
class Binding:
    """Not to be confused with Textual's Binding class"""

    key: str
    description: str
    group: str

    def bind(self, action: str) -> TextualBinding:
        return TextualBinding(self.key, action, self.description)


@dataclass
class Bindings:
    # General
    show_help: Binding = Binding("f1", "Show help", "General")
    open_file: Binding = Binding("alt+o", "Open File", "General")
    exit: Binding = Binding("alt+q", "Exit", "General")
    save: Binding = Binding("alt+s", "Save", "General")
    select_database: Binding = Binding("alt+d", "Select database", "General")

    # Editor
    execute_query: Binding = Binding("alt+enter", "Execute query", "Editor")
    autocomplete_open: Binding = Binding("alt+space", "Open autocomplete", "Editor")
    autocomplete_close: Binding = Binding("escape", "Close autocomplete", "Editor")
    autocomplete_apply: Binding = Binding("tab,enter", "Apply autocomplete", "Editor")
    format_query: Binding = Binding("alt+f", "Format query", "Editor")
    format_all: Binding = Binding("alt+shift+f", "Format all", "Editor")
    select_query: Binding = Binding("alt+shift+s", "Select query", "Editor")
    copy_selection: Binding = Binding("alt+c", "Copy selection", "Editor")
    switch_layout: Binding = Binding("alt+x", "Switch editor layout", "Editor")

    # Results
    export: Binding = Binding("alt+e", "Export results", "Results")
    toggle_cursor: Binding = Binding("alt+s", "Toggle cursor", "Results")

    # Tabs
    new_tab: Binding = Binding("alt+n", "New tab", "Tabs")
    close_tab: Binding = Binding("alt+w", "Close tab", "Tabs")
    next_tab: Binding = Binding("alt+tab,alt+pagedown", "Next tab", "Tabs")
    prev_tab: Binding = Binding("alt+shift+tab,alt+pageup", "Previous tab", "Tabs")
    show_tab_1: Binding = Binding("alt+1", "Switch to tab 1", "Tabs")
    show_tab_2: Binding = Binding("alt+2", "Switch to tab 2", "Tabs")
    show_tab_3: Binding = Binding("alt+3", "Switch to tab 3", "Tabs")
    show_tab_4: Binding = Binding("alt+4", "Switch to tab 4", "Tabs")
    show_tab_5: Binding = Binding("alt+5", "Switch to tab 5", "Tabs")
    show_tab_6: Binding = Binding("alt+6", "Switch to tab 6", "Tabs")
    show_tab_7: Binding = Binding("alt+7", "Switch to tab 7", "Tabs")
    show_tab_8: Binding = Binding("alt+8", "Switch to tab 8", "Tabs")
    show_tab_9: Binding = Binding("alt+9", "Switch to tab 9", "Tabs")
    show_tab_10: Binding = Binding("alt+0", "Switch to tab 10", "Tabs")

    def all(self) -> list[Binding]:
        return [getattr(self, f.name) for f in fields(self)]


def load_bindings() -> Bindings:
    user_keys = load_settings().get("bindings", {})

    bindings = Bindings()
    for field in fields(bindings):
        user_key = user_keys.get(field.name)
        if user_key and isinstance(user_key, str):
            default = field.default
            assert isinstance(default, Binding)
            binding = Binding(
                key=user_key,
                description=default.description,
                group=default.group,
            )
            setattr(bindings, field.name, binding)

    return bindings


bindings = load_bindings()
