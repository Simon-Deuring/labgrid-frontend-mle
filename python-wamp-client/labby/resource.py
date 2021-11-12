"""
Handle resources to be sent via the router
"""

class Resource:
    """
    Binds RPC for a resource
    """
    def __init__(self, name : str, **kwargs):
        self.name = name

    def publish(self, place : str, router):
        """
        publish a resource and its rpc to a router and place
        """
        raise NotImplementedError
