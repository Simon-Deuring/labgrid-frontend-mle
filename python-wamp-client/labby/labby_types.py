"""
Types used throughout labby
"""

from abc import abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from autobahn.asyncio.wamp import ApplicationSession
from attr import attrs, attrib

from labby.cache import Cache, CounterStrategy, PeriodicRefreshStrategy
from labby.console import Console
from labby.labby_ssh import Session as SSHSession


TargetName = str
ExporterName = str
PlaceName = str
ResourceName = str
GroupName = str
PlaceKey = Tuple[TargetName, PlaceName]
# Serializable labby arrer (LabbyError converted to json string)
SerLabbyError = Dict[str, Any]
Resource = Dict
Place = Dict
PowerState = Dict


async def get_places(context: "Session"):
    context.log.info("Refreshing Cache for places.")
    return await context.call("org.labgrid.coordinator.get_places")


async def get_resources(context: "Session"):
    context.log.info("Refreshing Cache for resources.")
    return await context.call("org.labgrid.coordinator.get_resources")


class Session(ApplicationSession):
    """
    Forward declaration for Labby session
    """

    def __init__(self, *args, **kwargs) -> None:
        self.resources: Cache[Resource] = Cache(data=None, refresh_data=get_resources, strategies=[
            CounterStrategy(5), PeriodicRefreshStrategy(60)])
        self.places: Cache[Place] = Cache(data=None, refresh_data=get_places, strategies=[  # type: ignore
            CounterStrategy(5), PeriodicRefreshStrategy(60)])
        self.acquired_places: Set[PlaceName] = set()
        self.power_states: Optional[List] = None
        self.reservations: Dict = {}
        self.to_refresh: Set = set()
        self.user_name: str
        self.open_consoles: Dict[PlaceName, Console] = {}
        self.ssh_session: SSHSession
        super().__init__(*args, **kwargs)


class LabbyType:
    @abstractmethod
    def to_json(self):
        """
        convert to json serializable dict
        """


@attrs
class LabbyPlace(LabbyType):
    name: str = attrib()
    acquired_resources: List[str] = attrib()
    exporter: str = attrib()
    power_state: bool = attrib()

    def to_json(self):
        return {
            "name": self.name,
            "acquired_resources": self.acquired_resources,
            "exporter": self.exporter,
            "power_state": self.power_state,
        }

# pylint: disable=invalid-name


class _ReservationState(Enum):
    waiting = 0
    allocated = 1
    acquired = 2
    expired = 3
    invalid = 4


@attrs
class LabbyReservation(LabbyType):
    owner: str = attrib(default=None,)
    token: str = attrib(default=None,)
    state: _ReservationState = attrib(default=None,)
    prio: float = attrib(default=None,)
    filters: Dict[str, Dict[str, str]] = attrib(default=None,)
    allocations: Dict[str, str] = attrib(default=None,)
    created: float = attrib(default=None,)
    timeout: float = attrib(default=None,)

    def place(self):
        return self.filters['main'].get('name', None)

    def to_json(self):
        return {
            'owner': self.owner,
            'state': self.state.name,
            'prio': self.prio,
            'filters': self.filters,
            'allocations': self.allocations,
            'created': self.created,
            'timeout': self.timeout,
        }
