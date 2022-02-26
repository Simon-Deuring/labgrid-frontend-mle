"""
Error Handling utility
"""

from enum import Enum
from typing import Optional

class ErrorKind(Enum):
    """
    Error keys, as defined in the API
    """
    INVALID_PARAMETER = "InvalidParameter"
    NOT_FOUND = "NotFound"
    FAILED = "Failed"


class LabbyError:
    """
    Helper for serializing Labby errors
    """

    def __init__(self, kind: ErrorKind, message: Optional[str] = None) -> None:
        self.kind = kind
        self.message = message

    def __repr__(self) -> str:
        return {
            "error": {
                "kind": self.kind.value,
                "message": self.message if self.message is not None else "",
            }
        }.__str__()

    def to_json(self):
        """
        Dump self as json; utility function
        """
        return {
            "error": {
                "kind": self.kind.value,
                "message": self.message if self.message is not None else "",
            }
        }


def invalid_parameter(message: str) -> LabbyError:
    """
    Factory method to instantiate InvalidParameter Error objects
    """
    assert message is not None
    return LabbyError(ErrorKind.INVALID_PARAMETER, message)


def not_found(message: str) -> LabbyError:
    """
    Factory method to instantiate NotFound Error objects
    """
    assert message is not None
    return LabbyError(ErrorKind.NOT_FOUND, message)


def failed(message: str) -> LabbyError:
    """
    Factory method to instantiate Failed Error objects
    """
    assert message is not None
    return LabbyError(ErrorKind.FAILED, message)
