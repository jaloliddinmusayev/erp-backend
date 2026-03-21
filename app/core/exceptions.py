"""Domain-level errors mapped to HTTP in route handlers."""


class NotFoundError(Exception):
    def __init__(self, detail: str = "Resource not found") -> None:
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str = "Conflict") -> None:
        self.detail = detail


class BusinessRuleError(Exception):
    """Invalid operation for current entity state (maps to HTTP 400)."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
