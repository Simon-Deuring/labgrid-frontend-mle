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

    def bind(self, *args, **kwargs):
        """
        Bind RPC to specific context, e.g LabbyClient Session, or pass immutables into func
        """
        return lambda *a, **kw: self.func(*args, *a, **kwargs, **kw)

    def bind_frontend(self, context: Callable, *args, **kwargs):
        """
        Bind RPC to specific context,to be called by the frontend
        """
        return lambda *a, **kw: self.func(context(), *args, *a, **kwargs, **kw)


async def places(context) -> List[str]:
    """
    returns registered places as dict of lists
    """
    context.log.info("Fetching places.")
    targets = await context.call("org.labgrid.coordinator.get_places")
    # first level is target
    return [{
        'name': name,
        'isRunning' : True,
        **target,
        # TODO (Kevin) field isRunning is not contained in places, consider issuing a second rpc call
    } for name, target in targets.items()]


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
            return {"resources": targets[target]}
        else:
            if not place in targets[target].keys():
                return le.not_found(f"Place {place} not found on Target").to_json()
            return {"resources": targets[target][place]}

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
