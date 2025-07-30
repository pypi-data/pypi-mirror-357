from textual.widget import Widget


class SwitchingLayout(Widget, inherit_bindings=False):
    """Container which alternates between horizontal and vertical layout."""

    DEFAULT_CSS = """
    SwitchingLayout {
        width: 1fr;
        height: 1fr;
        overflow: hidden hidden;
        layout: vertical;

        &.switched {
            layout: horizontal;
        }

        & > * {
            height: 1fr;
            width: 100%;
        }

        &.switched > * {
            height: 100%;
            width: 1fr;
        }
    }
    """

    def switch(self):
        self.toggle_class("switched")
