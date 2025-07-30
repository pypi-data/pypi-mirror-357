from itertools import chain

from psycopg.pq import TransactionStatus
from rich.style import Style
from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static

from pgtui.db import DbInfo


class DbFooter(Static):
    COMPONENT_CLASSES = {
        "dbfooter--dim",
        "dbfooter--highlight",
        "dbfooter--success",
        "dbfooter--error",
        "dbfooter--warning",
    }

    DEFAULT_CSS = """
    DbFooter {
        background: $primary;
        color: $text;
        dock: bottom;
        height: 1;
    }
    .dbfooter--dim       { color: $text; background: $background }
    .dbfooter--highlight { color: $text; background: $primary-darken-1 }
    .dbfooter--success   { color: $text; background: $success }
    .dbfooter--error     { color: $text; background: $error }
    .dbfooter--warning   { color: $text; background: $warning }
    """

    db_info: reactive[DbInfo | None] = reactive(None)
    tx_status: reactive[TransactionStatus | None] = reactive(None)
    running_query: reactive[bool] = reactive(False)

    def render(self):
        db_info = self.render_db_info()
        tx_status = self.render_tx_status()
        return Text.assemble(tx_status, *db_info)

    def render_db_info(self):
        if self.db_info is None:
            return [" Connecting to database..."]

        highlight = self.get_style("highlight")

        info = {
            "Database": self.db_info.database,
            "Schema": self.db_info.schema,
            "User": self.db_info.user,
            "Host": self.db_info.host,
            "Port": self.db_info.port,
            "Address": self.db_info.host_address,
        }

        return chain.from_iterable(
            [f" {name} ", (f" {value} ", highlight)] for name, value in info.items() if value
        )

    def render_tx_status(self):
        if self.running_query:
            return "  QUERYING  ", self.get_style("warning")

        match self.tx_status:
            case None:
                return ""
            case TransactionStatus.IDLE:
                return " IDLE ", self.get_style("dim")
            case TransactionStatus.ACTIVE:
                return " ACTIVE ", self.get_style("warning")
            case TransactionStatus.INTRANS:
                return " TRANSACTION ", self.get_style("success")
            case TransactionStatus.INERROR:
                return " ERROR ", self.get_style("error")
            case TransactionStatus.UNKNOWN:
                return " UNKNOWN ", self.get_style("error")

    def get_style(self, name: str) -> Style:
        return self.get_component_rich_style(f"dbfooter--{name}")
