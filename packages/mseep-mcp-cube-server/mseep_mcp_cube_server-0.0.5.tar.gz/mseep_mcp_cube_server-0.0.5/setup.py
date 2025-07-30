
from setuptools import setup, find_packages

setup(
    name="mseep-mcp_cube_server",
    version="0.0.5",
    description="MCP server for interfacing with Cube.dev REST API",
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
    install_requires=['mcp>=1.2.1', 'pandas', 'pyjwt>=2.10.1', 'python-dotenv', 'pyyaml>=6.0.2', 'requests>=2.32.3'],
    keywords=["mseep"] + [],
)
