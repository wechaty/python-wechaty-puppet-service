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
import os
from typing import Optional
from wechaty_puppet import get_logger

logger = get_logger('WechatyPuppetServiceConfig')

# send 1M data in every async request
CHUNK_SIZE = 1024 * 1024


TLS_CA_CERT = '''-----BEGIN CERTIFICATE-----
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
-----END CERTIFICATE-----'''


def get_token() -> Optional[str]:
    """
    get the token from environment variable
    """
    return os.environ.get('WECHATY_PUPPET_SERVICE_TOKEN', None) or \
        os.environ.get('TOKEN', None) or \
        os.environ.get('token', None) or None


def get_endpoint() -> Optional[str]:
    """
    get the endpoint from environment variable
    """
    return os.environ.get('WECHATY_PUPPET_SERVICE_ENDPOINT', None) or \
        os.environ.get('ENDPOINT', None) or \
        os.environ.get('endpoint', None) or None
