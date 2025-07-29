"""The python wrapper for IQ Option API package setup."""
from setuptools import (setup, find_packages)


setup(
    name="fx-iqoption",
    version="1.0.16",
    packages=find_packages(),
    install_requires=["pylint","requests","websocket-client>=0.56"],
    include_package_data=True,
    description="IQ Option API wrapper for Python",
    long_description="Python wrapper for IQ Option API with improved WebSocket handling and error management.",
    url="https://github.com/fxneiram/fx-iqoption",
    author="Faver Xavier Neira Molina",
    author_email="fxneiram@gmail.com",
    zip_safe=False
)
