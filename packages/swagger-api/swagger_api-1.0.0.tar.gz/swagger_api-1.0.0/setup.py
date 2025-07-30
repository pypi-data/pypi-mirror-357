from setuptools import setup

setup(
    name="swagger_api",
    version="1.0.0",
    author="HP Inc.",
    description="A tool to fetch and parse Swagger API definitions from a given URL.",
    packages=["swagger_api"],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "requests>=2.25.1",
        "mcp>=0.1.0"
    ],
)