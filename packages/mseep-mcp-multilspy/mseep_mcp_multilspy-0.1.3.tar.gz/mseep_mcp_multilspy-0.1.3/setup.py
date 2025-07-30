
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-multilspy",
    version="0.1.3",
    description="MCP server that exposes Language Server Protocol functionality via multilspy",
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
    install_requires=['mcp[cli]>=1.4.1', 'multilspy>=0.0.14'],
    keywords=["mseep"] + [],
)
