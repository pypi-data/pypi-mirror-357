
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-oceanbase",
    version="0.1.3",
    description="A Model Context Protocol (MCP) server that enables secure interaction with OceanBase databases. This server allows AI assistants to list tables, read data, and execute SQL queries through a controlled interface, making database exploration and analysis safer and more structured.",
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
    install_requires=['mcp[cli]>=1.0.0', 'fastmcp>=2.5.1', 'mysql-connector-python>=9.1.0', 'python-dotenv', 'beautifulsoup4>=4.13.3', 'certifi>=2025.4.26', 'requests'],
    keywords=["mseep"] + [],
)
