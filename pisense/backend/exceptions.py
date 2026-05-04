class DatabaseError(Exception):
    """Raised when database object runs into an issue."""
    def __init__(self, message: str):
        super().__init__(f"{message}") # Pass the formatted message to the base class

class DatabaseReconnectingError(DatabaseError):
    """Raised when database object disconnects from db, a reconnection has just been run."""

class UnauthorizedUserError(DatabaseError):
    """Raised when a user fails authentication."""

class FindingRowError(DatabaseError):
    """Raised when database can not find requested row or too many rows."""

class CouldNotConnectToDBError(DatabaseError):
    """Raised when the DB could not be accessed."""
