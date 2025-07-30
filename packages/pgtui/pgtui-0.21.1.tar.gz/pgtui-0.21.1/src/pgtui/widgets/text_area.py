from pgcli.pgcompleter import Completion  # type: ignore
from textual import events
from textual.document._document import Selection
from textual.document._edit import Edit
from textual.document._syntax_aware_document import SyntaxAwareDocument
from textual.message import Message
from textual.widgets import TextArea
from typing_extensions import override

from pgtui.bindings import bindings
from pgtui.messages import RunQuery
from pgtui.sql import find_query, format_sql


class Autocomplete:
    class Open(Message): ...

    class Close(Message): ...

    class Up(Message): ...

    class Down(Message): ...

    class PageUp(Message): ...

    class PageDown(Message): ...

    class Apply(Message): ...

    class Update(Message): ...


class SqlTextArea(TextArea):
    DEFAULT_CSS = """
    SqlTextArea {
        border: none;
        padding: 0 0 0 1;

        &:focus {
            border: none;
            background: $boost;
        }
    }
    """

    BINDINGS = [
        bindings.execute_query.bind("execute"),
        bindings.autocomplete_open.bind("autocomplete_open"),
        bindings.autocomplete_close.bind("autocomplete_close"),
        bindings.format_query.bind("format"),
        bindings.format_all.bind("format_all"),
        bindings.select_query.bind("select"),
        bindings.copy_selection.bind("copy"),
    ]

    def __init__(self, text: str = ""):
        super().__init__(text, language="sql")
        self.is_autocomplete_open = False

        # Can't use BINDINGS since we need to prevent the default action
        self.autocomplete_apply_keys = bindings.autocomplete_apply.key.split(",")

    # Triggered when cursor is moved, even if there's no selection
    def watch_selection(self, _: Selection, selection: Selection):
        has_selection = selection.start != selection.end
        if has_selection:
            self.post_message(Autocomplete.Close())
        else:
            self.post_message(Autocomplete.Update())

    def on_key(self, event: events.Key):
        if self.is_autocomplete_open:
            if event.key in self.autocomplete_apply_keys:
                self.post_message(Autocomplete.Apply())
                event.prevent_default()

    def action_autocomplete_open(self):
        self.post_message(Autocomplete.Open())

    def action_autocomplete_close(self):
        self.post_message(Autocomplete.Close())

    def on_blur(self, _):
        self.post_message(Autocomplete.Close())

    @override
    def action_cursor_up(self, select: bool = False):
        if self.is_autocomplete_open:
            self.post_message(Autocomplete.Up())
        else:
            super().action_cursor_up(select)

    @override
    def action_cursor_page_down(self):
        if self.is_autocomplete_open:
            self.post_message(Autocomplete.PageDown())
        else:
            super().action_cursor_page_down()

    @override
    def action_cursor_page_up(self):
        if self.is_autocomplete_open:
            self.post_message(Autocomplete.PageUp())
        else:
            super().action_cursor_page_up()

    @override
    def action_cursor_down(self, select: bool = False):
        if self.is_autocomplete_open:
            self.post_message(Autocomplete.Down())
        else:
            super().action_cursor_down(select)

    def action_execute(self):
        assert isinstance(self.document, SyntaxAwareDocument)
        if location := self.find_query():
            start, end = location
            query = self.text[start:end]
            self.post_message(RunQuery(query))

    def action_format(self):
        assert isinstance(self.document, SyntaxAwareDocument)
        if location := self.find_query():
            start, end = location
            query = self.text[start : end + 1]
            formatted = format_sql(query)
            start_location = self.document.get_location_from_index(start)
            end_location = self.document.get_location_from_index(end)
            edit = Edit(formatted, start_location, end_location, maintain_selection_offset=False)
            self.edit(edit)

    def action_format_all(self):
        text = format_sql(self.text)
        last_line = self.document.line_count - 1
        length_of_last_line = len(self.document[last_line])
        start = (0, 0)
        end = (last_line, length_of_last_line)
        edit = Edit(text, start, end, maintain_selection_offset=False)
        self.edit(edit)

    def action_select(self):
        assert isinstance(self.document, SyntaxAwareDocument)
        if location := self.find_query():
            start, end = location
            start_location = self.document.get_location_from_index(start)
            end_location = self.document.get_location_from_index(end)
            self.selection = Selection(start_location, end_location)

    def action_copy(self):
        if self.selected_text:
            self.app.copy_to_clipboard(self.selected_text)

    def find_query(self) -> tuple[int, int] | None:
        assert isinstance(self.document, SyntaxAwareDocument)

        # If a selection exists, return that
        if self.selected_text:
            if self.selected_text.strip():
                start = self.document.get_index_from_location(self.selection[0])
                end = self.document.get_index_from_location(self.selection[1])
                if end > start:
                    return start, end
                else:
                    return end, start
            else:
                # Empty selection
                return None

        # Do nothing if cursor is on an empty line
        [row, _] = self.cursor_location
        line = self.document.get_line(row)
        if line.strip() == "":
            return None

        index = self.document.get_index_from_location(self.cursor_location)

        # If cursor is positioned just after a query, then move cursor to
        # include that query.
        if self.cursor_at_end_of_line and self.text[index - 1 : index] == ";":
            index -= 1

        start, end = find_query(self.text, index)
        query = self.text[start : end + 1].strip()
        if not query:
            return None

        return start, end

    def apply_completion(self, completion: Completion):
        assert isinstance(self.document, SyntaxAwareDocument)

        end = self.document.get_index_from_location(self.cursor_location)
        end_loc = self.document.get_location_from_index(end)

        start = end + completion.start_position
        start_loc = self.document.get_location_from_index(start)

        self.edit(Edit(completion.text, start_loc, end_loc, maintain_selection_offset=False))
