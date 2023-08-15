# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ipymongodb",
    version="0.3.0",
    author="innovata sambong",
    author_email="iinnovata@gmail.com",
    description='pymongo 패키지 wrapper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/innovata/iPyMongo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"":"src"},
    packages=setuptools.find_packages("src"),
    python_requires=">=3.8",
    install_requires=['pymongo', 'pandas', 'ipylib'],
)
