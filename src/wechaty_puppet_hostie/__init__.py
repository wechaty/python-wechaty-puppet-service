"""
doc
"""
from wechaty_puppet import get_logger   # type: ignore
from wechaty_puppet_service import HostiePuppet

log = get_logger('WechatyPuppetHostie')

# TODO: this package will be deprecated after 0.6.10 version
log.warning(
    'package<wechaty_puppet_hostie> will be deprecated after 0.6.10, '
    'please import PuppetService from package<wechaty_puppet_service>'
)


__all__ = [
    'HostiePuppet'
]
