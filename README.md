# wechaty-puppet-service [![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/) [![PyPI GitHub Actions](https://github.com/wechaty/python-wechaty-puppet-service/workflows/PyPI/badge.svg)](https://github.com/wechaty/python-wechaty-puppet/actions?query=workflow%3APyPI)

[![Powered by Wechaty](https://img.shields.io/badge/Powered%20By-Wechaty-brightgreen.svg)](https://github.com/wechaty/wechaty)

![Service](https://wechaty.github.io/wechaty-puppet-service/images/hostie.png)

[![PyPI Version](https://img.shields.io/pypi/v/wechaty-puppet-service?color=blue)](https://pypi.org/project/wechaty-puppet-service)
![PyPI - Downloads](https://img.shields.io/pypi/dm/wechaty-puppet-service?color=blue)

Python Service Puppet for Wechaty

## Features

1. Consume Service service

## Usage

```python
import asyncio
from wechaty import Wechaty
from wechaty_puppet_service import PuppetService

bot = Wechaty(PuppetService("your-token-here"))
bot.on('message', lambda x: print(x))

asyncio.run(bot.start())
```

## Environment Variables

### 1 `WECHATY_PUPPET_SERVICE_TOKEN`

The token set to this environment variable will become the default value of `puppetOptions.token`

```sh
WECHATY_PUPPET_SERVICE_TOKEN=secret python bot.py
```

## History

### master

### v0.0.1 (Mar 10, 2020)

1. Init Python version
1. Published to PyPI

## Authors

- [@wj-Mcat](https://github.com/wj-Mcat) - Jingjing WU (吴京京)
- [@huan](https://github.com/huan) - ([李卓桓](http://linkedin.com/in/zixia)) zixia@zixia.net

## Copyright & License

* Code & Docs © 2020-now Huan LI \<zixia@zixia.net\>
* Code released under the Apache-2.0 License
* Docs released under Creative Commons
