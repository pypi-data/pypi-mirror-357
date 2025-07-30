
from setuptools import setup, find_packages

setup(
    name="mseep-beeper-mcp",
    version="0.1.3",
    description="a mcp server for interacting with chain",
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
    install_requires=['dotenv>=0.9.9', 'eth-account>=0.13.5', 'mcp[cli]>=1.4.1', 'pytest>=8.3.5', 'python-dotenv>=1.0.1', 'web3>=7.9.0', 'pyyaml>=6.0.1'],
    keywords=["mseep"] + [],
)
