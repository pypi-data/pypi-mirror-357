
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-rquest",
    version="0.1.16",
    description="A Model Context Protocol (MCP) server providing advanced HTTP request capabilities with realistic browser emulation for Claude and other LLMs",
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
    install_requires=['markdownify>=0.13.1,<0.14.0', 'mcp[cli]>=1.4.1', 'rnet>=2.0.0', 'tiktoken>=0.5.0', 'marker-pdf>=1.6.1'],
    keywords=["mseep"] + ['mcp', 'http', 'request', 'api', 'claude', 'llm', 'browser-emulation', 'tls-fingerprint', 'ja3', 'ja4', 'anti-bot'],
)
