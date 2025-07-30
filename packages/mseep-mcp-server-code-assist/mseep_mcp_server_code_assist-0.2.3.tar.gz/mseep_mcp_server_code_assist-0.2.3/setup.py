
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-code-assist",
    version="0.2.3",
    description="MCP Code Assist Server",
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
    install_requires=['aiofiles>=24.0.0', 'gitpython>=3.1.40', 'pydantic>=2.0.0', 'click>=8.1.7', 'mcp>=1.2.0', 'xmlschema>=3.4.3'],
    keywords=["mseep"] + [],
)
