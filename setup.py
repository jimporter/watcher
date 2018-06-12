import os
import platform
import re
import subprocess
import sys
from setuptools import setup, find_packages, Command

from watcher.version import version

root_dir = os.path.abspath(os.path.dirname(__file__))

custom_cmds = {}


with open(os.path.join(root_dir, 'README.md'), 'r') as f:
    long_desc = f.read()

try:
    import pypandoc
    long_desc = pypandoc.convert(long_desc, 'rst', format='md')
except ImportError:
    pass

try:
    from flake8.main.setuptools_command import Flake8

    class LintCommand(Flake8):
        def distribution_files(self):
            return ['setup.py', 'bfg9000', 'examples', 'test']

    custom_cmds['lint'] = LintCommand
except ImportError:
    pass


setup(
    name='watcher',
    version=version,

    description='A tool to watch for changes to webpages',
    long_description=long_desc,
    keywords='web page watcher',

    author='Jim Porter',
    author_email='itsjimporter@gmail.com',
    license='BSD',

    packages=find_packages(exclude=['test', 'test.*']),

    install_requires=(['cssselect', 'lxml', 'pyyaml']),
    extras_require={
        'dev': ['flake8 >= 3.0', 'pypandoc'],
        'test': ['flake8 >= 3.0'],
    },

    entry_points={
        'console_scripts': [
            'watcher=watcher.driver:main',
        ]
    },

    cmdclass=custom_cmds,
)
