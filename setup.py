"""
setup
"""
import semver
import setuptools


def versioning(version: str) -> str:
    """version to specification"""
    sem_ver = semver.parse(version)

    major = sem_ver['major']
    minor = sem_ver['minor']
    patch = str(sem_ver['patch'])

    if minor % 2:
        patch = 'dev' + patch

    fin_ver = '%d.%d.%s' % (
        major,
        minor,
        patch,
    )

    return fin_ver


def get_install_requires() -> str:
    """get install_requires"""
    with open('requirements.txt', 'r') as requirements_fh:
        return requirements_fh.read().splitlines()


def setup() -> None:
    """setup"""

    with open('README.md', 'r') as fh:
        long_description = fh.read()

    version = '0.0.0'
    with open('VERSION', 'r') as fh:
        version = versioning(fh.readline())

    setuptools.setup(
        name='wechaty-puppet-service',
        version=version,
        author='Huan LI (李卓桓)',
        author_email='zixia@zixia.net',
        description='Python Service Puppet for Wechaty',
        long_description=long_description,
        long_description_content_type='text/markdown',
        license='Apache-2.0',
        url='https://github.com/wechaty/python-wechaty-puppet-service',
        packages=setuptools.find_packages('src'),
        package_data={"wechaty_puppet_service": ["py.typed"]},
        package_dir={'': 'src'},
        install_requires=get_install_requires(),
        classifiers=[
            'Programming Language :: Python :: 3.7',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
        ],
    )


setup()
