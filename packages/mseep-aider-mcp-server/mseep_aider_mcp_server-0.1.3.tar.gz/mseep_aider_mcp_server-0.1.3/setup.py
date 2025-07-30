
from setuptools import setup, find_packages

setup(
    name="mseep-aider-mcp-server",
    version="0.1.3",
    description="Model context protocol server for offloading ai coding work to Aider",
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
    install_requires=['aider-chat>=0.81.0', 'boto3>=1.37.27', 'mcp>=1.6.0', 'pydantic>=2.11.2', 'pytest>=8.3.5', 'rich>=14.0.0'],
    keywords=["mseep"] + [],
)
