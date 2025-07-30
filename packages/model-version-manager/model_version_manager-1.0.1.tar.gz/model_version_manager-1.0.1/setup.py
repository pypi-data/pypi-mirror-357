from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()

setup(
    name="model_version_manager",
    version="1.0.1",
    author="Darkangel",
    author_email="llopnin@gmail.com",
    description="Makes it easier to work with versions for your projects.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    url="https://github.com/droid-darkangel/Version",

)