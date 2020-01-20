from os.path import dirname
from os.path import join

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand

from tornado_swagger import __version__

PACKAGE_NAME = 'tornado-swagger'
DESCRIPTION = 'Swagger API Documentation builder for tornado server'
HOME_URL = 'https://github.com/mrk-andreev/tornado-swagger'
DOWNLOAD_URL = 'https://pypi.org/project/tornado-swagger/#files'
MAINTAINER = 'Mark Andreev'
MAINTAINER_EMAIL = 'mark.andreev@gmail.com'
LICENSE = 'MIT License'
CLASSIFIERS = [
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

with open(join(dirname(__file__), 'requirements.txt')) as f:
    PACKAGES_REQUIRED = f.read().splitlines()

with open(join(dirname(__file__), 'README.md')) as f:
    LONG_DESCRIPTION = f.read()


class PyTest(TestCommand):
    user_options = []

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, '-m', 'pytest', 'tests'])
        raise SystemExit(errno)


def setup_package():
    setup(
        name=PACKAGE_NAME,
        version=__version__,
        install_requires=PACKAGES_REQUIRED,
        url=HOME_URL,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        packages=find_packages(),
        include_package_data=True,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        classifiers=CLASSIFIERS,
        tests_require=['pytest'],
        cmdclass=dict(test=PyTest)
    )


if __name__ == "__main__":
    setup_package()
