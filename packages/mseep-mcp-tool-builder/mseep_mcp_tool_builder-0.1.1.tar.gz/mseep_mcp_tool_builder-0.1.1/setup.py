
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-tool-builder",
    version="0.1.1",
    description="MCP server for dynamic tool creation",
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
    install_requires=['mcp', 'anthropic', 'python-dotenv', 'requests>=2.32.3', 'geopy'],
    keywords=["mseep"] + [],
)
