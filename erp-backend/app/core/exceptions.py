"""Domain-level errors mapped to HTTP in route handlers."""


class NotFoundError(Exception):
    def __init__(self, detail: str = "Resource not found") -> None:
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str = "Conflict") -> None:
        self.detail = detail
