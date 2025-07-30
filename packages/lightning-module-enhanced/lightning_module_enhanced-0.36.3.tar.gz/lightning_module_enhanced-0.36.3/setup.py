from setuptools import setup, find_packages
from os import path

name = "lightning-module-enhanced"
version = "0.36.3"
description = "Lightning Module Enhanced"
url = "https://gitlab.com/mihaicristianpirvu/lightning-module-enhanced"

loc = path.abspath(path.dirname(__file__))
with open(f"{loc}/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

required = ["torch>=2.5.1,<3.0.0", "pytorch_lightning==2.4.0", "torchinfo==1.8.0", "torchmetrics==1.4.1",
            "overrides==7.7.0", "matplotlib>=3.7.5", "loggez>=0.3", "pool-resources==0.3.0"]

setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    packages=find_packages(),
    install_requires=required,
    dependency_links=[],
    license="WTFPL",
    python_requires=">=3.10"
)
