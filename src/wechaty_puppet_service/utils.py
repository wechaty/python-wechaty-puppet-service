"""
Python Wechaty - https://github.com/wechaty/python-wechaty

Authors:    Huan LI (李卓桓) <https://github.com/huan>
            Jingjing WU (吴京京) <https://github.com/wj-Mcat>

2020-now @ Copyright Wechaty

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import annotations

from telnetlib import Telnet

import socket
from logging import Logger
from typing import Optional, Tuple
from ping3 import ping  # type: ignore
from wechaty_puppet.exceptions import WechatyPuppetConfigurationError  # type: ignore


def extract_host_and_port(url: str) -> Tuple[str, Optional[int]]:
    """it shoule be <host>:<port> format, but it can be a service name.
    If it's in docker cluster network, the port can be None

    Args:
        url (str): the service endpoint or names
    """
    if ':' in url:
        host, port = url.split(':')
        if not port.isdigit():
            raise WechatyPuppetConfigurationError(
                f'invalid endpoint: <{url}>'
            )
        return host, int(port)

    return url, None


def test_endpoint(end_point: str, log: Logger) -> int:
    """
        test_endpoint:
        1.If there is port: telnet
        2.If there is host/domain: ping or
    """
    tn = Telnet()
    host, port = extract_host_and_port(end_point)

    res = True
    if port is None:
        if ping(host) is False:
            res = False
    else:
        try:
            tn.open(host, port=port)
        except socket.error as e:
            log.error(e)
            res = False
    return res
