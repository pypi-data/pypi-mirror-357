
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-doris",
    version="0.1.4",
    description="An MCP server for Apache Doris.",
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
    install_requires=['mcp[cli]>=1.3.0', 'python-dotenv>=1.0.1', 'uvicorn>=0.34.0', 'pip-system-certs>=4.0', 'mysql-connector-python>=9.2.0'],
    keywords=["mseep"] + [],
)
