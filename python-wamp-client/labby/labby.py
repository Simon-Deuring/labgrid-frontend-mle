"""
A wamp client which registers a rpc function
"""
from autobahn.asyncio.component import Component,run

component = Component(
    transports=u"ws://localhost:8080/ws",
    realm='crossbardemo'
)

#dummy resource map
#TODO(Kevin) remove
resource_map : dict = {
    "place1" : ["video"],
    "place2" : ["video", "power_button"]
}

@component.on_join
def joined(session, details):
    print("session ready")

    def places() -> [str] :
        """
        returns registered places as list 
        """
        #TODO actually read places
        return {'places' : ["place1", "place2", "place3", "place4", "place5", ]}

    def resource(place : str):
        """
        rpc: returns resources registered for given place
        """
        #TODO(Kevin) do we need sanitization
        if place in resource_map.keys():
            return {'resource' : resource_map[place]}
        else:
            return "Invalid place or no resources for place"
        #TODO(Kevin) actually read resources for given place
        

    try:
        session.register(places, u'localhost.places')
        session.register(resource, u'localhost.resource')
        print("procedure registered")
    except Exception as e:
        print("could not register procedure: {0}".format(e))

if __name__ == '__main__':
    URL = "ws://localhost:8080/ws"
    REALM = "crossbardemo"
    
    run([component])
