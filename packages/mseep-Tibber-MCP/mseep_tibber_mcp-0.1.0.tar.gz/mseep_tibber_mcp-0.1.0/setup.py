
from setuptools import setup, find_packages

setup(
    name="mseep-Tibber_MCP",
    version="0.1.0",
    description="A Model Context Protocol (MCP) Server for Tibber, a Norwegian power supplier.",
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.5.0', 'pytibber>=0.30.8'],
    keywords=["mseep"] + [],
)
