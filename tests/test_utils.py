"""
unit test for utils module
"""
from wechaty_puppet_service.utils import (
    extract_host_and_port,
    ping_endpoint
)


def test_http_endpoint_extraction():
    endpoint = 'http://www.baidu.com'
    url, port = extract_host_and_port(endpoint)
    assert url == 'www.baidu.com'
    assert port == 80

    endpoint = 'https://www.baidu.com'
    url, port = extract_host_and_port(endpoint)
    assert port == 443


def test_ip_address_endpoint_extraction():
    endpoint = '127.0.0.1:80'
    url, port = extract_host_and_port(endpoint)
    assert url == '127.0.0.1'
    assert port == 80

    endpoint = '10.23.45.66:87'
    url, port = extract_host_and_port(endpoint)
    assert url == '10.23.45.66'
    assert port == 87


def test_ping_endpoint():
    valid_endpoint: str = 'https://www.baidu.com'
    assert ping_endpoint(valid_endpoint)

    invalid_endpoint: str = 'https://www.baidu.com:76'
    assert not ping_endpoint(invalid_endpoint)

    invalid_endpoint: str = 'https://www.abababa111111.com'
    assert not ping_endpoint(invalid_endpoint)
