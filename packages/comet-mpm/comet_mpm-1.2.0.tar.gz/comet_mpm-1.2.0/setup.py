#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

from pathlib import Path

from setuptools import find_packages, setup

requirements = [
    "pandas",
    "typing_extensions>=3.7.4",
    "aiohttp",
    "pydantic",
    "pydantic-settings",
    "requests",
]

# read the contents of your PACKAGE file

this_directory = Path(__file__).parent
long_description = (this_directory / "PACKAGE.md").read_text()


setup(
    author="Comet ML Inc.",
    author_email="mail@comet.ml",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3",
    ],
    description="Comet MPM SDK",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="comet_mpm",
    name="comet_mpm",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://www.comet.ml",
    version="1.2.0",
    zip_safe=False,
    license="Proprietary",
)
