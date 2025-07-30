
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-naa",
    version="0.1.3",
    description="An MCP server for Netwrix Access Analyzer",
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
    install_requires=['mcp[cli]>=1.5.0', 'pyodbc>=4.0.39', 'python-dotenv>=1.0.0'],
    keywords=["mseep"] + [],
)
