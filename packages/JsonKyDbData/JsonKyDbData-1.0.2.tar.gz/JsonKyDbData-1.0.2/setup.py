from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="JsonKyDbData",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[],
    author="hxk",
    # permit="",许可证
    author_email="xiaokang.he@foxmail.com",
    need="Python >=3.10",
    description="Store JSON data to a file!",
    long_description_content_type="text/markdown",
    long_description=long_description,
)
