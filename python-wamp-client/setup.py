from setuptools import setup


setup(
    name='labby',
    version='0.1.0',
    packages=['labby'],
    install_requires=[
        "autobahn[asyncio,serialization,encryption]==21.3.1",
        "crossbar",
        "pywin32==227 ; sys_platform == 'win32'",
        "setuptools",
    ]
)
