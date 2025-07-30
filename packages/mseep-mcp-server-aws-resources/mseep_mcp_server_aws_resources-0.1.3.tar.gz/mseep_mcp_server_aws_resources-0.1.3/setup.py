
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-aws-resources",
    version="0.1.3",
    description="MCP server for AWS resources using boto3",
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
    install_requires=['boto3', 'mcp', 'pydantic', 'pytz'],
    keywords=["mseep"] + [],
)
