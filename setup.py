from setuptools import setup

setup(
    name='qtile-alsavolumecontrol',
    packages=['alsavolumecontrol'],
    version='0.1.0',
    description='A module to control and display ALSA volume',
    author='elParaguayo',
    url='https://github.com/elparaguayo/qtile-alsavolumecontrol',
    license='MIT',
    install_requires=['qtile>0.14.2', 'pydbus']
)
