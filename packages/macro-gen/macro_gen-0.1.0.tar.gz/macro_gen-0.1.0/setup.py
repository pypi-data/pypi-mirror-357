from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="macro-gen",
    version="0.1.0",
    author="Ali Terro",
    author_email="aliterr588@gmail.com",
    description="A tool to record and replay mouse and keyboard actions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0xTristo/macro-gen",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "macro-gen=macro_gen.main:main",
            "macro-gen-install=macro_gen.install_config:main",
        ],
    },
    package_data={
        "macro_gen": ["macro_gen.conf"],
    },
    data_files=[
        ('share/man/man8', ['macro-gen.8']),
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pynput>=1.7.0",
        "configparser>=5.0.0",
    ],
)
