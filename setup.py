"""Setup module for the gsy-myco-sdk."""

import os

from setuptools import find_packages, setup

from gsy_myco_sdk import __version__

BRANCH = os.environ.get("BRANCH", "master")


try:
    with open("requirements/base.txt", encoding="utf-8") as req:
        REQUIREMENTS = [r.partition("#")[0] for r in req if not r.startswith("-e")]
        REQUIREMENTS.extend(
            ["gsy-framework @ "
             f"git+https://github.com/gridsingularity/gsy-framework.git@{BRANCH}"])

except OSError:
    # Shouldn't happen
    REQUIREMENTS = []


with open("README.md", "r", encoding="utf-8") as readme:
    README = readme.read()

# *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
VERSION = __version__

setup(
    name="gsy-myco-sdk",
    description="Myco API Client",
    long_description=README,
    author="GridSingularity",
    author_email="contact@gridsingularity.com",
    url="https://github.com/gridsingularity/gsy-myco-sdk",
    version=VERSION,
    packages=find_packages(where=".", exclude=["tests"]),
    package_dir={"gsy_myco_sdk": "gsy_myco_sdk"},
    package_data={},
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "gsy-myco-sdk = gsy_myco_sdk.cli:main",
            "myco = gsy_myco_sdk.cli:main"
        ]
    },
    zip_safe=False,
)
