
from setuptools import setup, find_packages

setup(
    name="mseep-mysqldb-mcp-server",
    version="0.1.5",
    description="An MCP server implementation for MySQL database integration",
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
    install_requires=['mcp>=1.4.1', 'mysql-connector-python>=9.2.0', 'python-dotenv>=1.0.1'],
    keywords=["mseep"] + [],
)
