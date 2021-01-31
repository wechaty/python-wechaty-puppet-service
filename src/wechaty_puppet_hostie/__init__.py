"""
doc
"""
from wechaty_puppet import get_logger   # type: ignore
from wechaty_puppet_service import PuppetService

log = get_logger('WechatyPuppetHostie')

# TODO: this package will be deprecated after 0.6.10 version
log.warning(
    'package<wechaty_puppet_hostie> will be deprecated after 0.6.10, '
    'please import PuppetService from package<wechaty_puppet_service>'
)


# TODO: this class should be removed after 0.6.10 version
class HostiePuppet(PuppetService):
    """Old HostiePuppet will be deprecated after 0.6.10 version"""
    def __init__(self, options, name='puppet-hostie'):
        super().__init__(options, name=name)

        log.warning('HostiePuppet object will be deprecated after 0.6.10 '
                    'version, please use PuppetService class as soon as '
                    'possible to avoid unnecessary bugs')


__all__ = [
    'HostiePuppet'
]
