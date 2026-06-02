import re
from os.path import dirname
from os.path import join

from setuptools import find_packages
from setuptools import setup

PACKAGE_NAME = "tornado-swagger"
DESCRIPTION = "Swagger API Documentation builder for tornado server"
HOME_URL = "https://github.com/mrk-andreev/tornado-swagger"
DOWNLOAD_URL = "https://pypi.org/project/tornado-swagger/#files"
MAINTAINER = "Mark Andreev"
MAINTAINER_EMAIL = "mark.andreev@gmail.com"
LICENSE = "MIT License"
CLASSIFIERS = [
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

with open(join(dirname(__file__), "requirements.txt"), encoding="utf-8") as f:
    PACKAGES_REQUIRED = f.read().splitlines()

with open(join(dirname(__file__), "README.rst"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

with open(join(dirname(__file__), "tornado_swagger", "__init__.py"), encoding="utf-8") as f:
    VERSION = re.search(r'__version__ = "([^"]+)"', f.read()).group(1)


def setup_package():
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
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
        classifiers=CLASSIFIERS,
    )


if __name__ == "__main__":
    setup_package()
