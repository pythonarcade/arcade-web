#! /usr/bin/env python
import os

from setuptools import find_namespace_packages, setup


def _rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def _get_version():
    dirname = os.path.dirname(__file__) or '.'
    my_path = f"{dirname}/arcade/VERSION"

    try:
        text_file = open(my_path, "r")
        data = text_file.read().strip()
        text_file.close()
        data = _rreplace(data, ".", "", 1)
        data = _rreplace(data, "-", ".", 1)
    except Exception:
        print(f"ERROR: Unable to load version number via '{my_path}'.")
        print(f"Files in that directory: {os.listdir(my_path)}")
        data = "0.0.0"

    return data

VERSION = _get_version()


def get_long_description() -> str:
    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    with open(fname, "r") as f:
        return f.read()


setup(
    name="arcade-web",
    description="A version of Arcade which allows running games in a browser",
    long_description=get_long_description(),
    author="Darren Eberly",
    author_email="darren.eberly@gmail.com",
    license="MIT",
    url="https://api.arcade.academy",
    download_url="https://api.arcade.academy",
    packages=find_namespace_packages(
        include=["arcade", "arcade.*"],
        exclude=[],
    ),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    project_urls={
        "Documentation": "https://api.arcade.academy/",
        "Example Code": "https://api.arcade.academy/en/latest/examples/index.html",
        "Issue Tracker": "https://github.com/pythonarcade/arcade-web/issues",
        "Source": "https://github.com/pythonarcade/arcade-web",
    },
    version=VERSION,
)