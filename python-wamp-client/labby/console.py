import asyncio
import getpass
import logging
from os import path
import sys
import threading
from typing import Any, Optional, Union

import paramiko
from attr import attrib, attrs
from paramiko import AuthenticationException, SSHException

logging.basicConfig(level=logging.DEBUG)

# enable "gssapi-with-mic" authentication, if supported by your python installation
UseGSSAPI = (paramiko.GSS_AUTH_AVAILABLE)
# enable "gssapi-kex" key exchange, if supported by your python installation
DoGSSAPIKeyExchange = (paramiko.GSS_AUTH_AVAILABLE)
# UseGSSAPI = False
# DoGSSAPIKeyExchange = False


@attrs
class Console:
    host: str = attrib()
    username: str = attrib()
    port: int = attrib(default=22)
    ssh: Optional[paramiko.SSHClient] = attrib(default=None, init=False)
    channel: Optional[paramiko.Channel] = attrib(default=None, init=False)
    key_file: Optional[str] = attrib(default=None)

    def open(self):
        if self.ssh:
            self.ssh.close()
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

        if UseGSSAPI or DoGSSAPIKeyExchange:
            try:
                self.ssh.connect(hostname=self.host,
                                 port=self.port,
                                 banner_timeout=60,
                                 timeout=60,
                                 auth_timeout=60,
                                 username=self.username,
                                 gss_auth=UseGSSAPI,
                                 gss_kex=DoGSSAPIKeyExchange,
                                 #  key_filename=path.join(
                                 #      path.expanduser("~"), ".ssh/id_rsa")
                                 )
            except (AuthenticationException, SSHException):
                self.ssh.connect(hostname=self.host,
                                 port=self.port,
                                 banner_timeout=60,
                                 timeout=60,
                                 auth_timeout=60,
                                 username=self.username,
                                 password=getpass.getpass(
                                     f"Password for {self.username}@{self.host}:{self.port} : "),
                                 key_filename=path.join(path.expanduser(
                                     "~"), self.key_file)
                                 )
        else:
            password = getpass.getpass(
                f"Password for {self.username}@{self.host}: ")
            self.ssh.connect(hostname=self.host,
                             port=self.port,
                             banner_timeout=100,
                             username=self.username,
                             password=password,

                             )
        # self.channel = self.ssh.invoke_shell()

    def microcom(self, host: str, port: int, speed: int):
        assert self.ssh
        return self.ssh.exec_command(f"microcom -s {speed} -t {host}:{port}")

    def close(self):
        if self.ssh:
            self.ssh.close()

    def send(self, data: str):
        assert not self.channel.closed, "Console not connected"
        assert self.channel, "No valid channel open"
        self.channel.sendall(bytes(data, 'utf-8'))

    def recv(self) -> str:
        assert not self.channel.closed, "Console not connected"
        assert self.channel, "No valid channel open"
        return self.channel.recv(1024).decode('utf-8')

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


def create_tx_callbacks(channel: paramiko.Channel, buffertype=bytes, consoleEOF=None):
    async def asread(nbytes=1024) -> Union[buffertype, Any]:
        if channel.closed:
            return consoleEOF
        data = await asyncio.get_event_loop().run_in_executor(None, channel.recv, nbytes)
        return data or consoleEOF

    async def aswrite(data: Union[str, bytes, Any]):
        if channel.closed:
            return consoleEOF
        if isinstance(data, str):
            data = bytes(data, encoding='utf-8')
        await asyncio.get_event_loop().run_in_executor(None, channel.sendall, data)

    return (aswrite, asread)


def create_tx_callbacks_mc(sin, sout, serr, buffertype=bytes, consoleEOF=None):

    def make_read(chan):
        async def asread(nbytes=1024) -> Union[buffertype, Any]:
            data = await asyncio.get_event_loop().run_in_executor(None, chan.read, nbytes)
            return data or consoleEOF
        return asread

    async def aswrite(data: Union[str, bytes, Any]):
        if isinstance(data, str):
            data = bytes(data, encoding='utf-8')
        await asyncio.get_event_loop().run_in_executor(None, sin.write, data)

    return (aswrite, make_read(sout), make_read(serr))


if __name__ == "__main__":
    host = sys.argv[1]
    username = sys.argv[2]
    port = int(sys.argv[3])
    key_file = sys.argv[4]
    mhost = sys.argv[5]
    mport = int(sys.argv[6])
    with Console(
        host=host,
        port=port,
        username=username,
        key_file=key_file
    ) as con:
        stdin, stdout, stderr = con.microcom(
            host=mhost, port=mport, speed=115200)
        # interactive_shell(con.channel)

        def writeall(sock):
            while True:
                data = sock.readline()
                if not data:
                    sys.stdout.write("\r\n*** EOF ***\r\n\r\n")
                    sys.stdout.flush()
                    break
                sys.stdout.write(data)
                sys.stdout.flush()

        writer = threading.Thread(target=writeall, args=(stdout,))
        writer.start()
        try:
            while True:
                data = sys.stdin.readline()
                if not data:
                    break
                stdin.write(data)
        except EOFError:
            # user hit ^Z or F6
            pass
