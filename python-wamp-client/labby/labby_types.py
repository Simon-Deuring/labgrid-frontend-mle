from typing import Tuple
from autobahn.asyncio.wamp import ApplicationSession

TargetName = str
PlaceName = str
ResourceName = str
GroupName = str
PlaceKey = Tuple[TargetName, PlaceName]
Session = ApplicationSession
