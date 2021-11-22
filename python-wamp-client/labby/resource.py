"""
Handle resources to be sent via the router
"""
from enum import Enum

class ResourceType(Enum):
    RawSerialPort = "RawSerialPort"
    NetworkSerialPort = "NetworkSerialPort"
    USBSerialPort = "USBSerialPort"
    PowerPorts = "PowerPorts"



def set_exporter_url(url : str):
    #TODO (Kevin)
    raise NotImplementedError

def get_exporter_url(url : str):
    #TODO (Kevin)
    raise NotImplementedError

class Resource:
    """
    Binds RPC for a resource
    """
    def __init__(self, **kwargs):
        self.raw_params = kwargs["params"]

    def publish(self, place : str, router):
        """
        publish a resource and its rpc to a router and place
        """
        raise NotImplementedError

    def is_available(self) -> bool:
        """
        Is the backed resource available to be used
        """
        raise NotImplementedError
