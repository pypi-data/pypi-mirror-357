
from setuptools import setup, find_packages

setup(
    name="mseep-alibaba-cloud-ops-mcp-server",
    version="0.9.8",
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
    install_requires=['alibabacloud-cms20190101>=3.1.4', 'alibabacloud-ecs20140526>=6.1.0', 'alibabacloud-oos20190601>=3.4.1', 'alibabacloud_oss_v2>=1.1.0', 'alibabacloud-credentials>=1.0.0', 'click>=8.1.8', 'fastmcp>=2.8.0'],
    keywords=["mseep"] + [],
)
