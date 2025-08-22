class ValidationError(Exception):
    def __init__(self, message: str, code: str | None = None, row: int | None = None):
        super().__init__(message)
        self.code = code
        self.row = row
