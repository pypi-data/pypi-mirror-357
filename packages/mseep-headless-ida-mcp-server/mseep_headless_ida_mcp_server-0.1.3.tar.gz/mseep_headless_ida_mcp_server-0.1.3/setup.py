
from setuptools import setup, find_packages

setup(
    name="mseep-headless-ida-mcp-server",
    version="0.1.3",
    description="Add your description here",
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
    install_requires=['dotenv>=0.9.9', 'fastmcp>=0.4.1', 'headless-ida>=0.6.1', 'mcp>=1.6.0', 'pytest>=8.3.5', 'pytest-asyncio>=0.26.0'],
    keywords=["mseep"] + [],
)
