class DSLError(Exception):
    """DSL hatalarının taban sınıfı."""

    code: str | None = None

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code


class DSLParseError(DSLError):
    pass


class DSLForbiddenNode(DSLError):
    pass


class DSLUnknownName(DSLError):
    pass


class DSLBadArgs(DSLError):
    pass
