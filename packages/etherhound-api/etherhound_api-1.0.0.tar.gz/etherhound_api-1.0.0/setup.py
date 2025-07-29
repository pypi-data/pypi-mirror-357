from setuptools import setup, find_packages

setup(
    name="etherhound-api",
    version="1.0.0",
    description="EtherHound API - API Client for EtherHound Core",
    long_description=open("readme.md", "r+").read(),
    author="SpicyPenguin",
    packages=find_packages(exclude=["tests", "examples"]),
    install_requires=[
        "pydantic",
        "aiohttp"
    ],
    python_requires=">=3.11"
)