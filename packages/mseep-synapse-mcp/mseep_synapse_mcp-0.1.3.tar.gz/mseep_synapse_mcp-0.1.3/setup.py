
from setuptools import setup, find_packages

setup(
    name="mseep-synapse-mcp",
    version="0.1.3",
    description="A Model Context Protocol (MCP) server that exposes Synapse Entities with Croissant metadata support",
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
    install_requires=['mcp[cli]>=1.3.0', 'requests>=2.32.3', 'synapseclient>=4.7.0', 'fastapi>=0.110.0', 'uvicorn>=0.27.0'],
    keywords=["mseep"] + ['synapse', 'mcp', 'croissant', 'metadata', 'bioinformatics'],
)
