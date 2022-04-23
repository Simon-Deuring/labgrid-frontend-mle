import asyncio
from typing import Union

import paramiko
from attr import attrs, field
from paramiko.channel import ChannelFile, ChannelStderrFile, ChannelStdinFile


def _read_flush(channel: Union[ChannelFile, ChannelStderrFile]):
    if channel.channel.closed or channel.channel.exit_status_ready():
        raise OSError("Channel closed")
    data = channel.readlines(1)  # read when at least one byte is written
    # convert to string and chop off extra new lines
    data = ''.join(map(lambda line: line[:-1], data))
    channel.flush()
    return data


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
        # from threading import Thread

        # def write_sin():
        #     while not self._sin.channel.exit_status_ready():
        #         data = input(">")
        #         self._sin.write(f"{data}\n")
        # Thread(target=write_sin).start()

    def write_to_stdin(self, data: str):
        assert self._sin
        data = data if data[-1] == '\n' else f"{data}\n"
        data_bytes: bytes = bytes(data, encoding='utf-8')
        self._sin.write(data_bytes)
        self._sin.flush()

    async def read_stdout(self) -> str:
        assert self._sout
        data = await asyncio.get_event_loop().run_in_executor(None, _read_flush, self._sout)
        return data

    async def read_stderr(self) -> str:
        assert self._serr
        data = await asyncio.get_event_loop().run_in_executor(None, _read_flush, self._serr)
        return data

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
        self._sin.channel.close()
        self._sout.channel.close()
        self._serr.channel.close()
