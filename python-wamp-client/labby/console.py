import asyncio

import paramiko
from attr import attrs, field
from paramiko.channel import ChannelFile, ChannelStderrFile, ChannelStdinFile


@attrs
class Console:
    _sin: ChannelStdinFile = field(init=False)
    _sout: ChannelFile = field(init=False)
    _serr: ChannelStderrFile = field(init=False)
    host: str = field()
    ssh_session: paramiko.SSHClient = field()
    speed: int = field(default=115200)
    port: int = field(default=22)

    def __attrs_post_init__(self):
        assert self.ssh_session
        (self._sin, self._sout, self._serr) = self.ssh_session.exec_command(
            f"microcom -s {self.speed} -t {self.host}:{self.port}")

    async def write_to_stdin(self, data: str):
        assert self._sin
        data_bytes: bytes = bytes(data, encoding='utf-8')
        await asyncio.get_event_loop().run_in_executor(None, self._sin.write, data_bytes)

    async def read_stdout(self, nbytes=1024) -> str:
        assert self._sout
        data = await asyncio.get_event_loop().run_in_executor(None, self._sout.read, nbytes)
        return data.decode('utf-8')

    async def read_stderr(self, nbytes=1024) -> str:
        assert self._serr
        data = await asyncio.get_event_loop().run_in_executor(None, self._serr.read, nbytes)
        return data.decode('utf-8')

    def close(self):
        if self._sin:
            self._sin.flush()
            self._sin.close()
        if self._sout:
            self._sout.flush()
            self._sout.close()
        if self._serr:
            self._serr.flush()
            self._serr.close()
