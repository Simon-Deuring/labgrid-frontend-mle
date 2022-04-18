"""
Handle ssh sessions for labby
- e.g hold a ssh session and allow new channels
to be created for remote communication with resources
"""

import logging
import urllib.parse
from collections.abc import Mapping
from typing import Any, Dict, List, Optional, Union

import paramiko
from attr import attrib, attrs, field
from paramiko import (AuthenticationException, SSHClient, SSHException,
                      WarningPolicy)

from labby.forward import forward_tunnel


@attrs
class _ShellOptions(Mapping):
    term: str = attrib()
    width: int = attrib()
    height: int = attrib()
    width_pixels: int = attrib()
    height_pixels: int = attrib()
    environment: Dict = attrib()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "term": self.term,
            "width": self.width,
            "height": self.height,
            "width_pixels": self.width_pixels,
            "height_pixels": self.height_pixels,
            "environment": self.environment,
        }

    def __iter__(self):
        return iter(self.to_dict())

    def __getitem__(self, item):
        return getattr(self, item)

    def __len__(self):
        return len(self.to_dict())


# enable "gssapi-with-mic" authentication, if supported by your python installation
UseGSSAPI = (paramiko.GSS_AUTH_AVAILABLE)
# enable "gssapi-kex" key exchange, if supported by your python installation
DoGSSAPIKeyExchange = (paramiko.GSS_AUTH_AVAILABLE)
# UseGSSAPI = False
# DoGSSAPIKeyExchange = False


def _validate_field(name):
    def validator(instance, attribute, value):
        if (x := len(value) > 0):
            return x
        else:
            raise ValueError(f"{name} must not be empty.")
    return validator


def _validate_port(instance, attribute, value):
    if not (0 <= value <= 65535):
        raise ValueError("Port must be integer between 0 and 65535")


@attrs
class Channel:
    channel: paramiko.Channel = attrib()

    def microcom(self, host: str, port: int, speed: int):
        """
        Open a serial console over microcom from an existing ssh channel
        """
        assert not self.channel.closed
        return self.channel.exec_command(f"microcom -s {speed} -t {host}:{port}")

    def close(self):
        self.channel.close()

    def exec_command(self, command: Union[str, bytes]):
        return self.channel.exec_command(command=command)


@attrs
class Tunnel:
    local_port: int = field()
    remote_host: str = field()
    remote_port: int = field()


@ attrs
class Session:
    """
    Wrapper for paramiko's SSH session, provides methods
    o create channels for remote communication with resources
    """
    host: str = attrib(validator=[_validate_field("Host")])
    username: str = attrib(validator=[_validate_field("Username")])
    keyfile_path: str = attrib(validator=[_validate_field("Keyfile")])
    port: int = attrib(default=22, validator=[_validate_port])
    opened_channels: List[Channel] = []
    forwarded_channels: List[Tunnel] = []
    client: Optional[SSHClient] = None
    _channel: Optional[paramiko.Channel] = None

    def _connect_with_keys(self, password=None):
        assert self.client
        try:
            self.client.connect(hostname=self.host,
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
            # yield to get password from higher context
            self.client.connect(hostname=self.host,
                                port=self.port,
                                banner_timeout=60,
                                timeout=60,
                                auth_timeout=60,
                                username=self.username,
                                password=password,
                                key_filename=self.keyfile_path)

    def open(self, password=None):
        if self.client:
            self.client.close()  # close if there was an open session
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(WarningPolicy())
        if UseGSSAPI or DoGSSAPIKeyExchange:
            self._connect_with_keys(password=password)
        else:
            self.client.connect(hostname=self.host,
                                port=self.port,
                                banner_timeout=100,
                                auth_timeout=60,
                                timeout=60,
                                username=self.username,
                                password=password)
        # self._channel = self._client.invoke_shell()

    def close(self) -> None:
        self.forwarded_channels.clear()
        for channel in self.opened_channels:
            channel.close()
        self.opened_channels.clear()
        if self.client:
            self.client.close()

    def create_channel(self, shell_options: Optional[_ShellOptions] = None) -> Channel:
        assert self.client
        _channel = self.client.invoke_shell(
        ) if shell_options is None else self.client.invoke_shell(**shell_options)
        channel = Channel(_channel)
        self.opened_channels.append(channel)
        return channel

    def forward(self, local_port: int, remote_host: str, remote_port: int):
        """
        Create and register a forwarded tcp channel over the ssh transport
        """
        assert self.client
        if (tunnel := Tunnel(local_port=local_port, remote_host=remote_host, remote_port=remote_port)) not in self.forwarded_channels:
            self.forwarded_channels.append(tunnel)
            forward_tunnel(local_port=local_port, remote_host=remote_host, remote_port=remote_port,
                           transport=self.client.get_transport())
        else:
            logging.info("Channel already forwarded")


def parse_hostport(urllike: str):
    # urlparse() and urlsplit() insists on absolute URLs starting with "//"
    if urllike.find("//") <= 0:
        urllike = f'//{urllike}'
    result = urllib.parse.urlsplit(urllike)
    return result.hostname, result.port, result.username
