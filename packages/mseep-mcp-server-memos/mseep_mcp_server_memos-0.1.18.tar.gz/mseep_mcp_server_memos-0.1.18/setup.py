
from setuptools import setup, find_packages

setup(
    name="mseep-mcp-server-memos",
    version="0.1.18",
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
    install_requires=['mcp>=1.1.0', 'betterproto[compiler]>=2.0.0b6', 'grpclib>=0.4.7', 'pydantic>=2.10.3'],
    keywords=["mseep"] + [],
)
