from enum import Enum
from typing import Optional, Union
from urllib.parse import urlparse

class Protocol(Enum):
    WS  = "ws"
    WSS = "wss"

    def __repr__(self) -> str:
        return "ws" if self.value == Protocol.WS else "wss"

def validate_uri(url : str):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def url_from_parts(
        protocol : Union[Protocol, str],
        user : Optional[str],
        domain : str,
        port : int,
        path : Optional[str]
        ) -> Optional[str]:
    if domain is None:
        return None
    protocol = protocol.value if isinstance(protocol, Protocol) else protocol
    user = "" if user is None else (user + ":")
    #domain = domain
    if (port.bit_length() > 16) or (port < 0):
        return None
    path = "" if path is None else path
    url = f"{protocol}://{user}{domain}:{port}/{path}"
    if not validate_uri(url):
        return None
    return url
