
from setuptools import setup, find_packages

setup(
    name="mseep-comfy-ui-mcp-server",
    version="0.1.0",
    description="MCP server for ComfyUI integration",
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
    install_requires=['mcp>=0.1.0', 'websockets>=12.0', 'aiohttp>=3.9.1', 'pydantic>=2.5.2', 'websocket-client>=1.8.0'],
    keywords=["mseep"] + [],
)
