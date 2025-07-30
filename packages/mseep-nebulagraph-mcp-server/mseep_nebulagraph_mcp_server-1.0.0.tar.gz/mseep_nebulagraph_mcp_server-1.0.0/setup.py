
from setuptools import setup, find_packages

setup(
    name="mseep-nebulagraph-mcp-server",
    version="1.0.0",
    description="A Model Context Protocol server providing tools to access NebulaGraph for usage by LLMs",
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
    install_requires=['mcp>=1.0.0', 'nebula3-python>=3.8.0', 'python-dotenv>=1.0.1'],
    keywords=["mseep"] + [],
)
