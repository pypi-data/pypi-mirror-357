
from setuptools import setup, find_packages

setup(
    name="mseep-rcon-mcp",
    version="0.1.4",
    description="A Model Context Protocol server for CS2 RCON management",
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
    install_requires=['rcon', 'mcp==1.3.0', 'python-dotenv==1.0.1', 'sse-starlette==2.2.1', 'starlette==0.46.0', 'uvicorn==0.34.0'],
    keywords=["mseep"] + [],
)
