
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-monday",
    version="0.2.12",
    description="MCP Server for monday.com",
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
    install_requires=['mcp[cli]>=1.2.1', 'monday>=2.0.1', 'requests>=2.32.3', 'ruff>=0.9.6'],
    keywords=["mseep"] + [],
)
