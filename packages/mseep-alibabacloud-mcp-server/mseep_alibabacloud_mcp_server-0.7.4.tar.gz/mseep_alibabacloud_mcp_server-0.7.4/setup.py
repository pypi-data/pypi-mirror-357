
from setuptools import setup, find_packages

setup(
    name="mseep-alibabacloud-mcp-server",
    version="0.7.4",
    description="A MCP server for Alibaba Cloud",
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
    install_requires=['alibabacloud-cms20190101>=3.1.4', 'alibabacloud-ecs20140526>=6.1.0', 'alibabacloud-oos20190601>=3.4.1', 'click>=8.1.8', 'mcp[cli]>=1.6.0'],
    keywords=["mseep"] + [],
)
