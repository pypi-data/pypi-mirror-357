
from setuptools import setup, find_packages

setup(
    name="mseep-adb-mysql-mcp-server",
    version="1.0.3",
    description="An offical mcp server for Adb MySQL of Alibaba Cloud",
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
    install_requires=['mcp[cli]>=1.5.0', 'pymysql>=1.1.1'],
    keywords=["mseep"] + [],
)
