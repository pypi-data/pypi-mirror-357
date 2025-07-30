
from setuptools import setup, find_packages

setup(
    name="mseep-mem0-mcp",
    version="0.1.4",
    description="MCP server for integrating long term memory into AI agents with Mem0",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.3.0', 'mem0ai>=0.1.88', 'vecs>=0.4.5'],
    keywords=["mseep"] + [],
)
