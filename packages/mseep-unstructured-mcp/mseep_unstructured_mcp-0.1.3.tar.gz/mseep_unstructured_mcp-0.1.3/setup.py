
from setuptools import setup, find_packages

setup(
    name="mseep-unstructured-mcp",
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
    install_requires=['boto3>=1.37.9', 'python-dotenv>=1.0.1', 'unstructured-client>=0.31.1', 'mcp[cli]>=1.3.0'],
    keywords=["mseep"] + [],
)
