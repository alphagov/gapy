import os
import sys
import gapy

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

try:
    long_description = open(
        os.path.join(os.path.dirname(__file__), 'README.rst')).read()
except:
    long_description = None

setup(
    name=gapy.__title__,
    version=gapy.__version__,
    description="Painless Google Analytics",
    long_description=long_description,
    author="Rob Young",
    author_email="rob@roryoung.co.uk",
    url="https://github.com/robyoung/gapy",
    packages=packages,
    package_dir={"gapy": "gapy"},
    include_package_data=True,
    install_requires=requires,
    license="https://raw.github.com/robyoung/gapy/master/LICENSE",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License"
    ]
)
