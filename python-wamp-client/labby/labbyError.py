from enum import Enum
from typing import Optional

class ErrorKind(Enum):
    InvalidParameter = "InvalidParameter"
    NotFound = "NotFound"

class LabbyError:

    def __init__(self, kind : ErrorKind, message : Optional[str] = None) -> None:
        self.kind = kind
        self.message = message

    def __repr__(self) -> str:
        return { "error" : {
                    "kind" : self.kind.value,
                    "message" : self.message if not (self.message  is None) else ""
                    }
                }.__str__()

