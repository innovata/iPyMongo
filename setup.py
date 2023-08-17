# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


with open("requirements.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()
    f.close()
    packages = text.split('\n')
    INSTALL_REQUIRES = [pack.strip() for pack in packages if len(pack.strip()) > 0]


PROJECT_PACKAGE_DIR = 'src'



setuptools.setup(
    name="ipymongodb",
    version="0.3.1",
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
    install_requires=INSTALL_REQUIRES,
)

