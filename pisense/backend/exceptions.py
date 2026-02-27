


class DatabaseError(Exception):
    """Raised when database object runs into an issue."""
    def __init__(self, message: str):
        super().__init__(f"{message}") # Pass the formatted message to the base class
