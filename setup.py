from setuptools import setup

from dwca_generator import __version__

setup(name='dwca_generator',
    version=__version__,
    description='Generator for extended/event-based DarwinCore-Archive files. ',
    url='https://github.com/sharkdata/darwincore',
    author='Arnold Andreasson',
    author_email='info@mellifica.se',
    license='MIT',
    packages=['dwca_generator'],
    install_requires=[
        'openpyxl', 
        'pytz', 
    ],
    zip_safe=False)