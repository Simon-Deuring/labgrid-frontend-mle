"""
A wamp client which registers a rpc function
"""
from autobahn.asyncio.component import Component,run
from typing import List, Dict, Optional

from .labbyError import LabbyError, ErrorKind

def get_resources() -> Dict[str, List[str]] :
    """
    Utility function to read currently available resources
    """

    return {
        "place1" : ["video"],
        "place2" : ["video", "power_button"]
    }

class LabbyClient:

    def __init__(self, realm : str, domain : str, port : int) -> None:
        self.realm = realm
        self.domain = domain
        self.port = port

        self.component = Component(
            transports=u"ws://{}:{}/ws".format(domain, port),
            realm=f'{realm}'
        )

        self.resource_map = get_resources()

    def run(self) -> None:
        @self.component.on_join
        def joined(session, details):
            print("session ready")

            def places() -> Dict[str, List[str]] :
                """
                returns registered places as dict of lists
                """
                #TODO actually read places
                return {'places' : ["place1", "place2", "place3", "place4", "place5", ]}

            def resource(place : Optional[str] = None):
                """
                rpc: returns resources registered for given place
                """
                #TODO(Kevin) do we need sanitization?
                if place is None:
                        return {'resources' : self.resource_map}
                    #TODO(Kevin) actually read resources for given place
                else:
                    if place in self.resource_map.keys():
                        return {'resources' : self.resource_map[place]}
                    else:
                        return LabbyError(ErrorKind.InvalidParameter, "Invalid place or no resources for place")
                    #TODO(Kevin) actually read resources for given place

            try:
                session.register(places, u'localhost.places')
                session.register(resource, u'localhost.resource')
                print("procedure registered")
            except Exception as e:
                print("could not register procedure: {0}".format(e))

        run([self.component])

def url_from_parts(domain : Optional[str], port : Optional[int], url : Optional[str] = None) -> Optional[str]:
    if domain is not None and port is not None:
        return f"ws://{domain}:{port}"


def run_server(realm : str, domain : str, port : int, url : str = None):
    labby = LabbyClient(realm, domain, port)
