from textual.message import Message


class RunQuery(Message):
    def __init__(self, query: str):
        self.query = query
        super().__init__()


class ShowException(Message):
    def __init__(self, exception: Exception):
        self.exception = exception
        super().__init__()
