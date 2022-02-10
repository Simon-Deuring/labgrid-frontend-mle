"""
Types used throughout labby
"""

from typing import Dict, List, Optional, Tuple
from autobahn.asyncio.wamp import ApplicationSession

TargetName = str
PlaceName = str
ResourceName = str
GroupName = str
PlaceKey = Tuple[TargetName, PlaceName]
SerLabbyError = Dict # Serializable labby arrer (LabbyError converted to json string)
Resource = Dict
Place = Dict
PowerState = Dict

class Session(ApplicationSession):
    """
    Forward declaration for Labby session
    """

    def __init__(self, *args, **kwargs) -> None:
        self.resources: Optional[Dict] = None
        self.places: Optional[Dict] = None
        self.acquired_places: List = []
        super().__init__(*args, **kwargs)
