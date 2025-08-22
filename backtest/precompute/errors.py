class PrecomputeError(Exception):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code
