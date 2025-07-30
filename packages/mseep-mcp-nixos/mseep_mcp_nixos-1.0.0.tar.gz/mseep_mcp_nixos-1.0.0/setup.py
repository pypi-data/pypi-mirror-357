
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-nixos",
    version="1.0.0",
    description="Model Context Protocol server for NixOS, Home Manager, and nix-darwin resources",
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
    install_requires=['mcp>=1.6.0', 'requests>=2.32.3', 'beautifulsoup4>=4.13.3'],
    keywords=["mseep"] + [],
)
