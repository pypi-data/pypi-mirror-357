from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="subnetcalc",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    author="recuero",
    description="A lightweight and efficient Python tool to perform subnetting operations on IPv4 addresses. It can be used both as a standalone CLI utility and as a reusable module in your Python projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/recuer0"
)

