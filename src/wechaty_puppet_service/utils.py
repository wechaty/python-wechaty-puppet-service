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
from typing import Tuple
from urllib.parse import urlsplit
from xml.dom import minidom

from wechaty_puppet import FileBox, WechatyPuppetError


def extract_host_and_port(url: str) -> Tuple[str, int]:
    """
    It should be <host>:<port> format, but it can be a service name.
    If it's in docker cluster network, the port can be None.

    Args:
        url (str): the service endpoint or names

    Return:
        host (str), port (int)
    """
    # 1. be sure that there is schema(http:// or https://) in endpoint
    if not url.startswith('http://') and not url.startswith('https://'):
        url = f'http://{url}'

    # 2. extract host & port from url
    split_result = urlsplit(url)
    host = split_result.hostname
    if not host:
        raise WechatyPuppetError(f'invalid url: {url}')

    default_port = 443 if split_result.scheme == 'https' else 80
    port = split_result.port or default_port

    return host, port


def ping_endpoint(end_point: str) -> bool:
    """
    Check end point is valid
    Use different method:
        1. If there is port: telnet
        2. If there is host/domain: ping

    Args:
        end_point (str): host and port

    Return:
        return True if end point is valid, otherwise False

    Examples:
        >>> end_point = '127.0.0.1:80'
        >>> assert ping_endpoint(end_point)

    """
    # 1. extract host & port
    tn = Telnet()
    host, port = extract_host_and_port(end_point)

    # 2. test host:port with socket
    res = True
    try:
        tn.open(host, port=port, timeout=3)
    except socket.error:
        res = False

    return res


async def message_emoticon(message: str) -> FileBox:
    """
    emoticon from message

    :param message:
    :return:
    """
    dom_tree = minidom.parseString(message)
    collection = dom_tree.documentElement
    file_box = FileBox.from_url(
        url=collection.getElementsByTagName('emoji')[0].getAttribute('cdnurl'),
        name=collection.getElementsByTagName('emoji')[0].getAttribute('md5') + '.gif'
    )
    return file_box
