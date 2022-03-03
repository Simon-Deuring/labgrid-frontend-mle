"""
Generic RPC functions for labby
"""

import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Type, Union

import yaml
from attr import attrib, attrs
from autobahn.wamp.exception import ApplicationError

from .labby_error import (ErrorKind, LabbyError, failed, invalid_parameter,
                          not_found)
from .labby_types import (LabbyPlace, PlaceName, PowerState, Resource,
                          ResourceName, Session)
from .labby_util import flatten, prepare_place


@attrs()
class RPCDesc():
    name: str = attrib(default=None)
    endpoint: str = attrib(default=None)
    remote_endpoint: str = attrib(default=None)
    info: Optional[str] = attrib(default=None)
    parameter: Optional[List[Dict[str, str]]] = attrib(default=None)
    return_type: Optional[str] = attrib(default=None)


def _localfile(path): return Path(os.path.dirname(
    os.path.realpath(__file__))).joinpath(path)


FUNCTION_INFO = {}
with open(_localfile('rpc_desc.yaml'), 'r', encoding='utf-8') as file:
    tmp = {key: RPCDesc(**val) for key, val in yaml.load(file,
                                                         yaml.loader.FullLoader).items() if val is not None}


# non exhaustive list of serializable primitive types
_serializable_primitive: List[Type] = [int, float, str, bool]

# TODO (Kevin) create a function to invalidate cache
def invalidate_cache(attribute):
    """
    on call clear attribute (e.g. set to None)
    """
    def decorator(func: Callable):
        pass

    return decorator


def cached(attribute: str):
    """
    Decorator defintion to cache data in labby context and fetch data from server
    """
    assert attribute is not None

    def decorator(func: Callable):

        async def wrapped(context: Session, *args, **kwargs):
            assert context is not None

            if not hasattr(context, attribute):
                context.__dict__.update({attribute: None})
                data = None
            else:
                data: Optional[Dict] = context.__getattribute__(
                    attribute)
            if context.__getattribute__(attribute) is None:
                data: Optional[Dict] = await func(context, *args, **kwargs)
                context.__setattr__(attribute, data)
            return data

        return wrapped

    return decorator


def labby_serialized(func):
    """
    Custom serializer decorator for labby rpc functions
    to make sure returned values are cbor/json serializable
    """
    async def wrapped(*args, **kwargs):
        ret = await func(*args, **kwargs)
        if isinstance(ret, LabbyError):
            return ret.to_json()
        if isinstance(ret, LabbyPlace):
            return ret.to_json()
        if isinstance(ret, (dict, list)) or type(ret) in _serializable_primitive:
            return ret
        raise NotImplementedError(
            f"{type(ret)} can currently not be serialized!")

    return wrapped


async def fetch(context: Session, attribute: str, endpoint: str, *args, **kwargs) -> Any:
    """
    QoL function to fetch data drom Coordinator and store in attribute member in Session
    """
    assert context is not None
    assert attribute is not None
    assert endpoint is not None

    data: Optional[Dict] = getattr(context, attribute)
    if data is None:
        data: Optional[Dict] = await context.call(endpoint, *args, **kwargs)
        setattr(context, attribute, data)
    return data


async def fetch_places(context: Session,
                       place: Optional[PlaceName]) -> Union[Dict, LabbyError]:
    """
    Fetch places from coordinator, update if missing and handle possible errors
    """
    assert context is not None
    data: Optional[Dict] = await fetch(context=context,
                                       attribute="places",
                                       endpoint="org.labgrid.coordinator.get_places")

    if data is None:
        if place is None:
            return not_found("Could not find any places.")
        return not_found(f"Could not find place with name {place}.")
    if place is not None and place not in data.keys():
        return not_found(f"Could not find place with name {place}.")

    return data


async def fetch_resources(context: Session,
                          place: Optional[PlaceName],
                          resource_key: Optional[ResourceName]) -> Union[Dict, LabbyError]:
    """
    Fetch resources from coordinator, update if missing and handle possible errors
    """
    assert context is not None
    data: Optional[Dict] = await fetch(context=context,
                                       attribute="resources",
                                       endpoint="org.labgrid.coordinator.get_resources")
    if data is None:
        if place is None:
            return not_found("Could not find any resources.")
        return not_found(f"No resources found for place {place}.")

    if resource_key is not None:
        ret = {
            place_name: {k: v for k, v in place_res if k == resource_key}
            for place_name, place_res in data.items()
        }

        if not ret:
            return not_found(f"Could not find any resources with key {resource_key}.")
        return ret
    return data


def _calc_power_for_place(place_name, resources: Iterable[Dict]):
    pstate = False
    for res in resources:
        if isinstance(res['acquired'], Iterable):
            pstate |= place_name in res['acquired']
        else:
            pstate |= res['acquired'] == place_name
    return pstate


@cached("power_states")
async def fetch_power_state(context: Session,
                            place: Optional[PlaceName]) -> Union[PowerState, LabbyError]:
    """
    Use fetch resource to determine power state, this may update context.resource
    """

    _resources = await fetch_resources(context=context, place=place, resource_key=None)
    if isinstance(_resources, LabbyError):
        return _resources
    if len(_resources) == 0:
        return not_found("No Places found.")
    _resources = flatten(_resources)
    _places = await fetch_places(context, place)
    if isinstance(_places, LabbyError):
        return _places
    power_states = {}
    for place_name, place_data in _places.items():
        if 'acquired_resources' in place_data:
            if len(place_data['acquired_resources']) == 0 or place_name not in _resources:
                power_states[place_name] = {'power_state': False}
                continue
            resources_to_check = ((v for k, v in _resources[place_name].items() if any(
                (k in a for a in place_data['acquired_resources']))))
            power_states[place_name] = {
                'power_state': _calc_power_for_place(place_name, resources_to_check)}
    return power_states


@labby_serialized
async def places(context: Session,
                 place: Optional[PlaceName] = None) -> Union[List[LabbyPlace], LabbyError]:
    """
    returns registered places as dict of lists
    """
    context.log.info("Fetching places.")

    data = await fetch_places(context, place)
    if isinstance(data, LabbyError):
        return data
    power_states = await fetch_power_state(context=context, place=place)
    assert power_states is not None
    if isinstance(power_states, LabbyError):
        return power_states
    place_res = []
    for place_name, place_data in data.items():
        if place is not None and place_name != place:
            continue
        # ??? (Kevin) what if there are more than one or no matches
        exporter = place_data["matches"][0]["exporter"]
        assert exporter is not None
        place_res.append(
            prepare_place(place_data, place_name, exporter,
                          power_states[place_name]['power_state'])
        )
    return place_res


@labby_serialized
async def resource(context: Session,
                   place: Optional[PlaceName] = None,
                   ) -> Union[Dict[ResourceName, Resource], LabbyError]:
    """
    rpc: returns resources registered for given place
    """
    context.log.info(f"Fetching resources for {place}.")
    resource_data = await fetch_resources(context=context, place=place, resource_key=None)

    if isinstance(resource_data, LabbyError):
        return resource_data

    if place is None:
        return resource_data
    if place not in resource_data.keys():
        return not_found(f"Place {place} not found.")
    return resource_data[place]


@labby_serialized
async def power_state(context: Session,
                      place: PlaceName,
                      ) -> Union[PowerState, LabbyError]:
    """
    rpc: return power state for a given place
    """
    # TODO (Kevin) Cache resource updates and get powerstates from there
    if place is None:
        return invalid_parameter("Missing required parameter: place.").to_json()
    power_data = await fetch_power_state(context=context, place=place)
    assert power_data is not None
    if isinstance(power_data, LabbyError):
        return power_data.to_json()

    if place not in power_data.keys():
        return not_found(f"Place {place} not found on Coordinator.").to_json()

    return power_data[place]


@labby_serialized
async def resource_overview(context: Session,
                            place: Optional[PlaceName] = None,
                            ) -> Union[List[Resource], LabbyError]:
    """
    rpc: returns list of all resources on target
    """
    context.log.info(f"Fetching resources overview for {place}.")

    targets = await fetch_resources(context=context, place=place, resource_key=None)
    if isinstance(targets, LabbyError):
        return targets

    ret = []
    for target, resources in targets.items():
        for res_place, res in resources.items():
            if place is None or place == res_place:
                ret.extend({'name': key, 'target': target,
                            'place': res_place, **values} for key, values in res.items())
    return ret


@labby_serialized
async def resource_by_name(context: Session,
                           name: ResourceName,  # filter by name
                           ) -> Union[List[Resource], LabbyError]:
    """
    rpc: returns list of all resources of given name on target
    """

    if name is None:
        return invalid_parameter("Missing required parameter: name.")

    resource_data = await fetch_resources(context, place=None, resource_key=None)
    if isinstance(resource_data, LabbyError):
        return resource_data

    ret = []
    for target, resources in resource_data.items():
        for place, res in resources.items():
            ret.extend(
                {'name': key, 'target': target, 'place': place, **values}
                for key, values in res.items()
                if name == key
            )

    return ret


@labby_serialized
async def acquire(context: Session,
                  place: PlaceName) -> Union[bool, LabbyError]:
    """
    rpc for acquiring places
    """
    if place is None:
        return invalid_parameter("Missing required parameter: place.")
    if place in context.acquired_places:
        return failed(f"Already acquired place {place}.")

    # , group, resource_key, place)
    context.log.info(f"Acquiring place {place}.")
    try:
        acquire_successful = await context.call("org.labgrid.coordinator.acquire_place", place)
    except ApplicationError as err:
        return failed(f"Got exception while trying to call org.labgrid.coordinator.acquire_place. {err}")
    if acquire_successful:
        context.acquired_places.append(place)
    return acquire_successful


@labby_serialized
async def release(context: Session,
                  place: PlaceName) -> Union[bool, LabbyError]:
    """
    rpc for releasing 'acquired' places
    """
    if place is None:
        return invalid_parameter("Missing required parameter: place.")
    if place not in context.acquired_places:
        return failed(f"Place {place} is not acquired")
    context.log.info(f"Releasing place {place}.")
    try:
        release_successful = await context.call('org.labgrid.coordinator.release_place', place)
    except ApplicationError as err:
        return failed(f"Got exception while trying to call org.labgrid.coordinator.release_place. {err}")
    if release_successful:
        context.acquired_places.remove(place)
    return release_successful


@labby_serialized
async def info(_context=None, func_key: Optional[str] = None) -> Union[List[Dict], LabbyError]:
    """
    RPC call for general info for RPC function usage
    """
    if func_key is None:
        return [desc.__dict__ for desc in globals()["FUNCTION_INFO"].values()]
    if func_key not in globals()["FUNCTION_INFO"]:
        return not_found(f"Function {func_key} not found in registry.")
    return globals()["FUNCTION_INFO"][func_key].__dict__


async def reservations(context: Session) -> Dict:
    """
    RPC call to list current reservations on the Coordinator
    """
    reservation_data = await context.call("org.labgrid.coordinator.get_reservations")
    # TODO (Kevin) handle errors
    return reservation_data


async def reset(context: Session, place: PlaceName) -> bool:
    """
    Send a reset request to a place matching a given place name
    Note 
    """
    return False


async def console(context: Session, *args):
    pass


async def video(context: Session, *args):
    pass


async def forward(context: Session, *args):
    """
    Forward a rpc call to the labgrid coordinator
    """
    return context.call(*args)


@labby_serialized
async def create_place(context: Session, place: PlaceName) -> Union[bool, LabbyError]:
    """
    Create a new place on the coordinator
    """
    assert place  # not None or empty
    places = fetch_places(context, place)
    if isinstance(places, LabbyError):
        if places.kind == ErrorKind.NOT_FOUND:
            return failed(f"Place {place} already exists on Coordinator")
        else:
            return places
    res = await context.call("org.labgrid.coordinator.add_place", place)
    return res


async def delete_place(context: Session, place: PlaceName) -> bool:
    return False


async def create_resource(context: Session, place: PlaceName, resource: Resource) -> bool:
    return False


async def delete_resource(context: Session, place: PlaceName, resource: ResourceName) -> bool:
    return False
