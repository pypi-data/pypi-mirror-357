
from setuptools import setup, find_packages

setup(
    name="mseep-terraform-cloud-mcp",
    version="0.8.12",
    description="A Model Context Protocol (MCP) server that integrates Claude with the Terraform Cloud API, allowing Claude to manage your Terraform infrastructure through natural conversation.",
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
    install_requires=['dotenv>=0.9.9', 'httpx>=0.28.1', 'mcp[cli]>=1.4.1'],
    keywords=["mseep"] + [],
)
