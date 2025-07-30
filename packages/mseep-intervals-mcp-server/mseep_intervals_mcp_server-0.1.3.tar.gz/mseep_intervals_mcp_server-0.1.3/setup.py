
from setuptools import setup, find_packages

setup(
    name="mseep-intervals-mcp-server",
    version="0.1.3",
    description="A Model Context Protocol server for Intervals.icu",
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
    install_requires=['mcp[cli]>=1.4.0', 'httpx>=0.25.0', 'python-dotenv>=1.0.0'],
    keywords=["mseep"] + ['intervals', 'cycling', 'running', 'mcp', 'ai'],
)
