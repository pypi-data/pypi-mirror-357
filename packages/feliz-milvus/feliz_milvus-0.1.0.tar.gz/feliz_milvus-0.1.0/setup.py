from setuptools import setup, find_packages

setup(
    name="feliz_milvus",
    version="0.1.0",
    description="A Python package for Milvus Git integration",
    author="nexuni",
    author_email="chewei.lee@nexuni.com",
    url="https://github.com/nexuni/feliz_milvus.git",
    packages=find_packages(),
    install_requires=[
        "pymilvus>=2.3.0",
        "numpy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)