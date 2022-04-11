"""
Handle resources to be sent via the router
"""
from enum import Enum
from typing import Dict, Optional
from attr import attrs, attrib


class ResourceType(Enum):
    RAWSERIALPORT = "RawSerialPort"
    NETWORKSERIALPORT = "NetworkSerialPort"
    USBSERIALPORT = "USBSerialPort"
    POWERPORTS = "PowerPorts"


@attrs
class LabbyResource:
    cls: Optional[str] = attrib()
    avail: bool = attrib(default=True)
    params: Dict = attrib(default=None)
    acquired: bool = attrib(default=False)

    def __init__(self, **kwargs):
        self.props = kwargs["params"]

    @property
    def name(self):
        return self.props["name"]


@attrs
class NetworkSerialPort(LabbyResource):
    port: int = attrib(default=12345)
    speed: int = attrib(default=115200)
    protocol: str = attrib(default='rfc2217')
    host: Optional[str] = attrib(default=None)
