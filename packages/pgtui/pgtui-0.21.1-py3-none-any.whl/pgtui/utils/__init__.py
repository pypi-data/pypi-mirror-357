from uuid import uuid4

from textual_fspicker import Filters


def random_id():
    return f"id_{uuid4().hex}"


def sql_filters():
    return Filters(
        ("SQL", lambda p: p.suffix.lower() == ".sql"),
        ("Any", lambda _: True),
    )
