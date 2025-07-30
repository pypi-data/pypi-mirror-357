
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server",
    version="0.1.4",
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
    install_requires=['bs4>=0.0.2', 'httpx>=0.28.1', 'mcp[cli]>=1.4.1', 'openai>=1.66.3'],
    keywords=["mseep"] + [],
)
