from textual.widgets import ContentSwitcher, TabbedContent, TabPane, Tabs

from pgtui.bindings import bindings


class SwitchingTabbedContent(TabbedContent):
    BINDINGS = [
        bindings.show_tab_1.bind("switch_tab(0)"),
        bindings.show_tab_2.bind("switch_tab(1)"),
        bindings.show_tab_3.bind("switch_tab(2)"),
        bindings.show_tab_4.bind("switch_tab(3)"),
        bindings.show_tab_5.bind("switch_tab(4)"),
        bindings.show_tab_6.bind("switch_tab(5)"),
        bindings.show_tab_7.bind("switch_tab(6)"),
        bindings.show_tab_8.bind("switch_tab(7)"),
        bindings.show_tab_9.bind("switch_tab(8)"),
        bindings.show_tab_10.bind("switch_tab(9)"),
        bindings.next_tab.bind("next_tab"),
        bindings.prev_tab.bind("prev_tab"),
    ]

    def action_switch_tab(self, no: int):
        panes = self._query_panes()
        if no < len(panes):
            pane = panes[no]
            assert pane.id is not None
            self.active = pane.id

    def action_next_tab(self):
        self._query_tabs().action_next_tab()

    def action_prev_tab(self):
        self._query_tabs().action_previous_tab()

    def _query_panes(self):
        cs = self.query_children(ContentSwitcher).first()
        return cs.query_children(TabPane)

    def _query_tabs(self) -> Tabs:
        return self.query_children(Tabs).first()
