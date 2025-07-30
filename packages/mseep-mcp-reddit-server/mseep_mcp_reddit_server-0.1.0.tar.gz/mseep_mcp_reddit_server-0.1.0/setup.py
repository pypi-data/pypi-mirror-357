
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-reddit-server",
    version="0.1.0",
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
    install_requires=['dnspython>=2.7.0', 'praw>=7.8.1', 'redditwarp>=1.3.0', 'fastmcp>=0.1.0', 'uvicorn'],
    keywords=["mseep"] + [],
)
