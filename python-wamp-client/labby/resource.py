"""
Handle resources to be sent via the router
"""
from enum import Enum
from typing import Dict, Optional
from attr import attrs, attrib, field


power_resources = [
    "NetworkPowerPort",
    "PDUDaemonPort",
    "NetworkUSBPowerPort",
    "NetworkSiSPMPowerPort",
    "TasmotaPowerPort",
]


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


class PowerAction(Enum):
    on = 0
    off = 1
    cycle = 2


ActionUrl = str


class PowerResource(LabbyResource):
    def power(self, action: PowerAction):
        raise NotImplementedError()


@attrs
class NetworkPowerPort(PowerResource):
    pass


class PDUDaemonPort(PowerResource):

    @attrs
    class Params:
        host: str = field()
        index: int = field()
        pdu: str = field()
        port: int = field(default=16421)
    params: Params

    @classmethod
    def params_from_dict(cls, params: Dict):
        return cls.Params(host=params.get('host'),
                          index=params.get('index'),
                          pdu=params.get('pdu'),
                          port=params.get('port', 16421))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = PDUDaemonPort.params_from_dict(kwargs['params'])

    def power(self, action: PowerAction):
        if action.value == PowerAction.cycle.value:
            return self.cycle_power()

    def cycle_power(self) -> ActionUrl:
        return f"http://{self.params.host}:{self.params.port}/power/control/reboot?hostname={self.params.pdu}&port={self.params.index}"


class NetworkUSBPowerPort(PowerResource):
    pass


class NetworkSiSPMPowerPort(PowerResource):
    pass


class TasmotaPowerPort(PowerResource):
    pass


def power_resource_from_name(name: str, data: dict) -> PowerResource:
    if name == "PDUDaemonPort":
        return PDUDaemonPort(**data)
    raise ValueError("Name not in supported list of Power Resources.")
