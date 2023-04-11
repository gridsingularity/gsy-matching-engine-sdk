"""Setup module for the gsy-matching-engine-sdk."""

import os

from setuptools import find_packages, setup

from gsy_matching_engine_sdk import __version__

GSY_FRAMEWORK_BRANCH = os.environ.get("GSY_FRAMEWORK_BRANCH", "master")


try:
    with open("requirements/base.txt", encoding="utf-8") as req:
        REQUIREMENTS = [r.partition("#")[0] for r in req if not r.startswith("-e")]
        REQUIREMENTS.extend(
            ["gsy-framework @ "
             f"git+https://github.com/gridsingularity/gsy-framework.git@{GSY_FRAMEWORK_BRANCH}"])

except OSError:
    # Shouldn't happen
    REQUIREMENTS = []


with open("README.md", "r", encoding="utf-8") as readme:
    README = readme.read()

# *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
VERSION = __version__

setup(
    name="gsy-matching-engine-sdk",
    description="Matching Engine API Client",
    long_description=README,
    author="GridSingularity",
    author_email="contact@gridsingularity.com",
    url="https://github.com/gridsingularity/gsy-matching-engine-sdk",
    version=VERSION,
    packages=find_packages(where=".", exclude=["tests"]),
    package_dir={"gsy_matching_engine_sdk": "gsy_matching_engine_sdk"},
    package_data={},
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "gsy-matching-engine-sdk = gsy_matching_engine_sdk.cli:main",
            "matching-engine = gsy_matching_engine_sdk.cli:main"
        ]
    },
    zip_safe=False,
)
