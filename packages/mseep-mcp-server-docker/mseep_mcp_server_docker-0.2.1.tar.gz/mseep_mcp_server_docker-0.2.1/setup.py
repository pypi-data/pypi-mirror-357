
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-docker",
    version="0.2.1",
    description="A Docker MCP Server",
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
    install_requires=['docker>=7.1.0', 'mcp>=1.1.0,<2.0', 'paramiko>=3.5.1,<4.0', 'pydantic>=2.10.3', 'pydantic-settings>=2.6.1'],
    keywords=["mseep"] + ['docker', 'mcp', 'server'],
)
