
from setuptools import setup, find_packages

setup(
    name="mseep-microsoft_sql_server_mcp",
    version="0.1.0",
    description="A Model Context Protocol (MCP) server that enables secure interaction with Microsoft SQL Server databases.",
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
    install_requires=['mcp>=1.0.0', 'pymssql>=2.2.8'],
    keywords=["mseep"] + ['mcp', 'mssql', 'sql-server', 'database', 'ai'],
)
