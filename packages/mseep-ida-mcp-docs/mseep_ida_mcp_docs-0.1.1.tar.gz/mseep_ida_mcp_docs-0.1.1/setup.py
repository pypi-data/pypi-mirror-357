
from setuptools import setup, find_packages

setup(
    name="mseep-ida-mcp-docs",
    version="0.1.1",
    description="IDA Pro MCP Documentation and Utilities",
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
    install_requires={'python': '^3.8', 'mcp': {'extras': ['cli'], 'version': '^0.1.0'}},
    keywords=["mseep"] + [],
)
