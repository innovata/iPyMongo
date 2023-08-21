# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


PROJECT_PACKAGE_DIR = 'src'



setuptools.setup(
    name="ipymongodb",
    version="0.4.0",
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
    package_dir={"": PROJECT_PACKAGE_DIR},
    packages=setuptools.find_packages(PROJECT_PACKAGE_DIR),
    python_requires=">=3.8",
    install_requires=[
        'pymongo','pandas','ipylib'
    ],
)

