from setuptools import setup, find_packages

setup(
    name="thiruklib1",
    version="0.0.1",
    author="thiru",
    author_email="thirukguru@gmail.com",
    description="this is the package for greeting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/thiruk/thiruklib1", #optional
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"],
    )