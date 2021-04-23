"""unit test for token environemnt"""
from __future__ import annotations

import os

from wechaty_puppet_service.config import get_token


def test_service_token():
    token = 'your-self-token'
    os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = token
    assert get_token() == token


def test_upper_token_name():
    token = 'your-self-token'
    os.environ['TOKEN'] = token
    assert get_token() == token


def test_lower_token_name():
    token = 'your-self-token'
    os.environ['token'] = token
    assert get_token() == token


def test_none_token():
    del os.environ['WECHATY_PUPPET_SERVICE_TOKEN']
    del os.environ['TOKEN']
    del os.environ['token']
    assert get_token() is None
