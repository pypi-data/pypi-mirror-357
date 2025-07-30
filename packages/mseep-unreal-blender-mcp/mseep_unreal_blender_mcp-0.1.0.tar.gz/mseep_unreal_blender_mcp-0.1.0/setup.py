
from setuptools import setup, find_packages

setup(
    name="mseep-unreal-blender-mcp",
    version="0.1.0",
    description="Unified MCP server for controlling Blender and Unreal Engine via AI agents",
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
    install_requires=['fastapi>=0.103.1', 'uvicorn>=0.23.2', 'sse-starlette>=1.6.5', 'langchain>=0.0.292', 'aiohttp>=3.8.5', 'langchain-community>=0.0.1', 'mcp[cli]>=1.3.0'],
    keywords=["mseep"] + [],
)
