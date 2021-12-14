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

    def bind(self, *args, **kwargs) -> Callable:
        """
        Bind RPC to specific context, e.g LabbyClient Session, or pass immutables into func
        """
        return lambda *a, **kw: self.func(*args, *a, **kwargs, **kw)

    def bind_frontend(self, context: Callable, *args, **kwargs) -> Callable:
        """
        Bind RPC to specific context,to be called by the frontend
        """
        return lambda *a: self.func(context(), *args, *a, **kwargs)


async def places(context, place: Optional[str] = None) -> List[Dict]:
    """
    returns registered places as dict of lists
    """
    context.log.info("Fetching places.")
    targets = await context.call("org.labgrid.coordinator.get_places")
    # first level is target
    if place is None:
        return [{
            'name': name,
            'isRunning': True,
            **target,
            # TODO (Kevin) field isRunning is not contained in places, consider issuing a second rpc call
        } for name, target in targets.items()]
    else:
        if not place in targets.keys():
            return le.not_found(f"Place {place} not found.")
        else:
            return [{
                'name': place,
                'isRunning': True,
                **targets[place],
                # TODO (Kevin) field isRunning is not contained in places, consider issuing a second rpc call
            }]


async def resource(context,
                   place: Optional[str] = None,
                   # TODO (Kevin) REPRESENT TARGET IN API
                   target: Union[str, int, None] = None,
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
                      place: str,
                      target: Union[str, int]
                      ) -> Dict:
    """
    rpc: return power state for a given place
    """
    if place is None:
        return le.invalid_parameter("Missing required parameter: place.").to_json()
    if target is None:
        return le.invalid_parameter("Missing required parameter: target.").to_json()
    resources = await resource(context, place, target)
    # a little hacky
    # FIXME (Kevin) don't serialize in rpc functions
    if "error" in resources.keys():
        return resources
    # TODO(Kevin) at the moment there is no way to do this any other way
    # hacky way to check power state, just see if any resource in place is available
    for res in resources.values():
        if "avail" in res.keys():
            return {"place": place, "power_state": bool(res["avail"])}
    return {"place": place, "power_state": False}


async def resource_overview(context,
                            place: Optional[str],
                            # TODO (Kevin) REPRESENT TARGET IN API
                            target: Union[str, int, None],
                            ) -> Dict:
    """
    rpc: returns list of all resources on target
    """
    context.log.info(f"Fetching resources overview for {target}.")
    
    targets = await context.call("org.labgrid.coordinator.get_resources")
    ret = []
    for target, resources in targets.items():
        for res_place, res in resources.items():
            if place is None or place == res_place:
                for k,v in res.items():
                        ret.append({'name' : k, 'target':target, 'place' : res_place, **v})
    return ret

async def resource_by_name(context,
                           name: str = None,  # filter by name
                           # TODO (Kevin) REPRESENT TARGET IN API
                           ) -> Dict:
    """
    rpc: returns list of all resources of given name on target
    """

    targets = await context.call("org.labgrid.coordinator.get_resources")
    ret = []
    for target, resources in targets.items():
        for place, res in resources.items():
            for k,v in res.items():
                if name is None or name == k:
                    ret.append({'name' : k, 'target':target, 'place' : place, **v})

    return ret
