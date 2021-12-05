"""
Start/stop/manage crossbar router
"""
import subprocess


class Router:
    """
    wrapper around subprocess.popen to be used in a async way
    """

    def __init__(self, path : str):
        """
        Starts a childprocess running the crossbar python module with the config file in <path>,
        usign the settings from that config file
        @parameter path: Path to .crossbar directory containig the crossbar config config.json file
        """
        self.process = subprocess.Popen(["crossbar", "start", "--cbdir", path])

    def stop(self):
        """
        Stop and wait until Router process has stopped
        """
        self.process.terminate()
        self.process.wait()



if __name__ == "__main__":
    try:
        p = subprocess.Popen(["crossbar", "start", "--cbdir", "labby/router/.crossbar"])
        p.wait()
    except KeyboardInterrupt:
        p.terminate()
