from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyTenSort",
    version="1.0.0",
    author="hxk",
    author_email="xiaokang.he@foxmail.com",
    need="Python >=3.10",
    description="Python Top 10 Sorting Algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[],
)
