import json
import os

import setuptools
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

with open(os.path.join('ucarball', 'analysis', 'PROTOBUF_VERSION'), 'r') as f:
    PROTOBUF_VERSION = json.loads(f.read())


with open(os.path.join('ucarball_VERSION'), 'r') as f:
    subversion = json.loads(f.read())

version_string = '0.' + str(PROTOBUF_VERSION) + '.' + str(subversion)

if os.path.isfile('README.md'):
    with open("README.md", "r") as readme_file:
        long_description = readme_file.read()
else:
    long_description = ''


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        from init import initialize_project
        initialize_project()
        # this needs to be last
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        from init import initialize_project
        initialize_project()
        # this needs to be last
        install.run(self)


setup(
    name='ucarball',
    version=version_string,
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas>=2.3.0',
        'protobuf>=4.21.0',
        'xlrd>=2.0.0',
        'numpy>=1.23.0',
        'uboxcars-py==0.1.*'
    ],
    url='https://github.com/SaltieRL/ucarball',
    keywords=['rocket-league'],
    license='Apache 2.0',
    author='AirwolfTomato, sciguymjm, and contributors',
    author_email='vijay@ashokn.org',
    description='Rocket League replay parsing and analysis.',
    long_description=long_description,
    exclude_package_data={'': ['.gitignore', '.git/*', '.git/**/*', 'replays/*']},
    long_description_content_type='text/markdown',
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    entry_points={
        'console_scripts': ['ucarball=ucarball.command_line:main']
    }
)
