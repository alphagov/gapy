import os
import sys

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

if sys.argv[-1] == "publish":
  os.system("python setup.py sdist upload")
  sys.exit()

packages = [
  "gapy"
]

requires = [
  "google-api-python-client==1.0",
  "pyOpenSSL==0.13"
]

setup(
  name="gapy",
  version="0.0.1",
  description="Painless Google Analytics",
  long_description=open("README.md").read(),
  author="Rob Young",
  url="https://github.com/robyoung/gapy",
  packages=packages,
  package_dir={"gapy":"gapy"},
  include_package_data=True,
  install_requires=requires,
  license=open("LICENSE").read(),
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Programming Language :: Python"
    "License :: OSI Approved :: MIT License"
  ]
)