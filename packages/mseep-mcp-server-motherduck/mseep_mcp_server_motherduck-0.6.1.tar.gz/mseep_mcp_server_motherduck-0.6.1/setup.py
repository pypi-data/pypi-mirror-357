
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-motherduck",
    version="0.6.1",
    description="A MCP server for MotherDuck and local DuckDB",
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author="mseep",
    author_email="support@skydeck.ai",
    maintainer="mseep",
    maintainer_email="support@skydeck.ai",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['duckdb==1.3.0', 'tabulate>=0.9.0', 'click>=8.1.8', 'starlette>=0.46.1', 'uvicorn>=0.34.0', 'anyio>=4.8.0', 'mcp>=1.9.4'],
    keywords=["mseep"] + [],
)
