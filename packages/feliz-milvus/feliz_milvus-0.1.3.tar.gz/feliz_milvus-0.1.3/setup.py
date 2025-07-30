from setuptools import setup, find_packages

setup(
    name="feliz-milvus",
    version="0.1.3",
    description="A Python package for Milvus Git integration",
    author="nexuni",
    author_email="chewei.lee@nexuni.com",
    url="https://github.com/nexuni/feliz_milvus",
    packages=find_packages(), 
    install_requires=[
        "pymilvus>=2.3.0",
        "numpy"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
