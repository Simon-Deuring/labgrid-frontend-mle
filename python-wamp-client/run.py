import labby
from labby import LabbyError, ErrorKind, run_server



if __name__ == '__main__':
    URL = "ws://localhost:8080/ws"
    REALM = "crossbardemo"
    run_server(REALM, "localhost", port=8080)
