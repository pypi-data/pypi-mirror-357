
from setuptools import setup, find_packages

setup(
    name="mseep-code2prompt-mcp",
    version="0.1.3",
    description="MCP server for Code2Prompt",
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
    install_requires=['mcp>=1.4.1', 'httpx>=0.28.1', 'dotenv>=0.9.9', 'colorlog>=6.9.0', 'code2prompt-rs>=3.2.1'],
    keywords=["mseep"] + [],
)
