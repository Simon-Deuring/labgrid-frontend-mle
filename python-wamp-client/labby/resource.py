"""
Handle resources to be sent via the router
"""
from enum import Enum
from typing import Dict


class ResourceType(Enum):
    RAWSERIALPORT = "RawSerialPort"
    NETWORKSERIALPORT = "NetworkSerialPort"
    USBSERIALPORT = "USBSerialPort"
    POWERPORTS = "PowerPorts"


def set_exporter_url(url: str):
    #TODO (Kevin)
    raise NotImplementedError


def get_exporter_url(url: str):
    #TODO (Kevin)
    raise NotImplementedError


class Resource:
    """
    Binds RPC for a resource
    """

    def __init__(self, **kwargs):
        self.raw_params = kwargs["params"]

    @property
    def name(self):
        return self.raw_params["name"]

    def publish(self, place: str, router):
        """
        publish a resource and its rpc to a router and place
        """
        raise NotImplementedError

    def is_available(self) -> bool:
        """
        Is the backed resource available to be used
        """
        raise NotImplementedError


def resource_from_ws(payload: Dict) -> Resource:
    assert "params" in payload
    return Resource()


if __name__ == "__main__":

    payload = {
        "name": "name",
        "matches": "",
        "acquired": False,
        "cls": ""
    }

    resource_from_ws(payload)
