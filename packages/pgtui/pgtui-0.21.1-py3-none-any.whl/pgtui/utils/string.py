def fit(string: str, length: int):
    if len(string) > length:
        return string[: length - 1] + "…"

    if len(string) < length:
        return string.ljust(length)

    return string
