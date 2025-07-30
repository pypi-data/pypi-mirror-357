import sqlparse  # type: ignore


def format_sql(sql: str) -> str:
    return sqlparse.format(sql.strip(), reindent=True)  # type: ignore


def find_query(text: str, index: int) -> tuple[int, int]:
    start = _search_backward(text, index)
    end = _search_forward(text, index)
    return start, end


def _search_forward(text: str, start: int):
    end = len(text)
    for offset in range(start, end):
        if text[offset : offset + 1] == ";":
            return offset + 1
        if text[offset : offset + 2] == "\n\n":
            return offset
    return end


def _search_backward(text: str, start: int):
    for offset in range(start - 1, -1, -1):
        if text[offset : offset + 2] == ";\n":
            return offset + 2
        if text[offset : offset + 1] == ";":
            return offset + 1
        if text[offset : offset + 2] == "\n\n":
            return offset + 2
    return 0
