from .labby_types import *


def prepare_place(place_data: Dict,
                  place_name: Optional[str] = None,
                  exporter: Optional[str] = None,
                  power_state: Optional[bool] = None):
    place_data.update({
        "name" : place_name,
        "exporter": exporter,
        "power_state" : power_state
    })
    return place_data
