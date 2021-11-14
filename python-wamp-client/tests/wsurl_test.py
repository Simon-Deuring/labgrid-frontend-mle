import unittest
from labby.wsurl import url_from_parts, Protocol
import random

def rand_ip() -> str:
    return ".".join([str(random.randint(0,255)) for _ in range(4)])

class TestUrlParse(unittest.TestCase):

    def setUp(self) -> None:
        # random.seed(1337)
        pass

    def test_url_parse_fuzzy(self) -> None:
        for _ in range(100):
            protocol = random.choice([Protocol.WS, Protocol.WSS, "ws", "wss"])
            user = random.choice([None, f"user{random.randint(0,1000)}"])
            domain = random.choice(["localhost", "127.0.0.1", 
                rand_ip(),
                "google.com",]
            )
            port=random.randint(0, 0xffff)
            path = random.choice([
                None,
                "path/to/res"
            ])
            self.assertIsNotNone(
                url_from_parts(
                    protocol=protocol,
                    user=user,
                    domain=domain,
                    port=port,
                    path=path
                )
            , "invalid url")

if __name__ == '__main__':
    unittest.main()