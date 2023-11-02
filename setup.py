import os
import sys
sys.path.insert(0, os.path.abspath('./src/'))

import setuptools

import easyo2p

# ---

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# ---

setuptools.setup(
    name = "easyo2p",
    version = easyo2p.__version__,
    author = "rikfair",
    author_email = "mail4rik-pypi@yahoo.com",
    description = "Oracle to PostgreSQL migration for Python",
    long_description=read('README.rst'),
    long_description_content_type = "text/x-rst",
    url = "https://github.com/rikfair/easyo2p",
    project_urls = {
        "Bug Tracker": "https://github.com/rikfair/easyo2p/issues",
        "Documentation": "https://easyo2p.readthedocs.io/"
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Database",
        "Topic :: Utilities"
    ],
    license = "MIT",
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.10",
)
