from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()

setup(
    name="upd_logger",
    version="1.0.0",
    author="Darkangel",
    author_email="llopnin@gmail.com",
    description="A feature-rich logging solution with file rotation, size-based cleanup, and configurable formatting.",
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
    url="https://github.com/droid-darkangel/upd_logger",

)