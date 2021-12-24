"""
Generic RPC functions for labby
"""

from typing import List, Dict, Union, Optional, Callable

import labby.labby_error as le


class RPC():
    """
    Wrapper for remote procedure call functions
    """

    def __init__(self, endpoint: str, func: Callable):
        assert not endpoint is None
        assert not func is None
        self.endpoint = endpoint
        self.func = func

    def __repr__(self):
        from inspect import signature

        sig = signature(self.func)
        ret_type = sig.return_annotation
        params = sig.parameters
        return f"{self.endpoint}\
            ({', '.join([f'{x.name}:{x.annotation}'for x in params.values()])}) -> {ret_type}"

    def bind(self, context: Callable, *args, **kwargs):
        """
        Bind RPC to specific context,to be called by the frontend
        """

        return lambda *a, **kw: self.func(*args, *a, context=context(), **kwargs, **kw)


async def places(context, place: Optional[str] = None) -> Union[List[Dict], Dict]:
    """
    returns registered places as dict of lists
    """
    context.log.info("Fetching places.")
    targets = await context.call("org.labgrid.coordinator.get_places")
    # first level is target

    async def get_item_power(name) -> Dict:
        power = await power_state(context=context, place=name, target='cup')
        # FIXME (Kevin) don't serialize in rpc functions
        if "error" in power.keys():
            # raise RuntimeError(power)
            return {"place": place, "power_state": False} # TODO (Kevin) handle error correctly
        return power

    if place is None:
        try:
            return [{
                'name': name,
                'isRunning': await get_item_power(name),
                **target,
            } for name, target in targets.items()]
        except RuntimeError as error:
            if len(error.args) > 0 and isinstance(error.args[0], Dict) and 'error' in error.args[0].keys():
                return error.args[0]
            raise error
    else:
        try:
            if not place in targets.keys():
                return le.not_found(f"Place {place} not found.").to_json()
            else:
                ret = [{
                    'name': place,
                    'isRunning': await get_item_power(place),
                    **targets[place],
                }]
                return ret
        except RuntimeError as error:
            if len(error.args) > 0 and isinstance(error.args[0], Dict) and 'error' in error.args[0].keys():
                return error.args[0]
            raise error


async def resource(context,
                   # TODO (Kevin) REPRESENT TARGET IN API
                   target: Union[str, int, None] = None,
                   place: Optional[str] = None,
                   ) -> Dict:
    """
    rpc: returns resources registered for given place
    """
    context.log.info(f"Fetching resources for {target}.{place}.")
    targets = await context.call("org.labgrid.coordinator.get_resources")

    def resource_for_place():
        if place is None:
            return targets[target]
        else:
            if not place in targets[target].keys():
                return le.not_found(f"Place {place} not found on Target").to_json()
            return targets[target][place]

    if isinstance(target, str):
        if not target in targets:
            err_str = f"Target {target} not found on Coordinator"
            context.log.warn(err_str)
            return le.not_found(err_str).to_json()
        return resource_for_place()

    elif isinstance(target, int):
        if target >= len(targets):
            err_str = f"Target {target} not found on Coordinator"
            context.log.warn(err_str)
            return le.not_found(err_str).to_json()
        return resource_for_place()

    return {"resources": targets}


async def power_state(context,
                      target: Union[str, int],
                      place: str,
                      ) -> Dict:
    """
    rpc: return power state for a given place
    """
    if place is None:
        return le.invalid_parameter("Missing required parameter: place.").to_json()
    if target is None:
        return le.invalid_parameter("Missing required parameter: target.").to_json()
    resources = await resource(context, place, target)
    # FIXME (Kevin) don't serialize in rpc functions
    if "error" in resources.keys():
        return resources

    # TODO(Kevin) at the moment there is no way to do this any other way
    # hacky way to check power state, just see if any resource in place is available
    for res in resources.values():
        if "avail" in res.keys():
            return {"place": place, "power_state": bool(res["avail"])}
    return {"place": place, "power_state": False}


async def acquire(context, target, place: str, resource : str, cls) -> Dict:
    """
    rpc for acquiring places
    """
    if target is None:
        return le.invalid_parameter("Missing required parameter: target.").to_json()
    if place is None:
        return le.invalid_parameter("Missing required parameter: place.").to_json()

    ret = await context.call(f"org.labgrid.exporter.{target}.acquire", resource, place, place)
    return ret # TODO (Kevin) figure out the failure modes


async def release(context, target, place: str, resource : str) -> Dict:
    """
    rpc for releasing 'acquired' places
    """
    if target is None:
        return le.invalid_parameter("Missing required parameter: target.").to_json()
    if place is None:
        return le.invalid_parameter("Missing required parameter: place.").to_json()
    if resource is None:
        return le.invalid_parameter("Missing required parameter: resource.").to_json()

    ret = await context.call(f"org.labgrid.exporter.{target}.release",  resource, place)
    return ret # TODO (Kevin) figure out the failure modes
