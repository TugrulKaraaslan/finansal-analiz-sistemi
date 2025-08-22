class NormalizeError(Exception):
    code: str | None = None
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code

class CollisionError(NormalizeError):
    pass

class AliasHeaderError(NormalizeError):
    pass
