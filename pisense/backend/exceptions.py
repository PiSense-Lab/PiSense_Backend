


class DatabaseError(Exception):
    """Raised when database object runs into an issue."""
    def __init__(self, message: str):
        super().__init__(f"{message}") # Pass the formatted message to the base class

class DatabaseReconnectingError(Exception):
    """Raised when database object disconnects from db, a reconnection has just been runs into an issue."""
    def __init__(self, message: str):
        super().__init__(f"{message}") # Pass the formatted message to the base class

class UnauthorizedUserError(Exception):
    """Raised when a user fails authentication."""
    def __init__(self, message: str):
        super().__init__(f"{message}") # Pass the formatted message to the base class

class FindingRowError(Exception):
    """Raised when a user fails authentication."""
    def __init__(self, message: str):
        super().__init__(f"{message}")
