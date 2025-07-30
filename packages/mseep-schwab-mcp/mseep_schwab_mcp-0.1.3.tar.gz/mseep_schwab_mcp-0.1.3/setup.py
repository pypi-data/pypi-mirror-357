
from setuptools import setup, find_packages

setup(
    name="mseep-schwab-mcp",
    version="0.1.3",
    description="Schwab Model Context Protocol (MCP) for the Schwab API",
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
    install_requires=['anyio>=4.9.0', 'click>=8.1.8', 'mcp>=1.4.1', 'platformdirs>=4.3.7', 'pyyaml>=6.0.2'],
    keywords=["mseep"] + [],
)
