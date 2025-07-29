from setuptools import setup, find_packages
import subprocess
import os

version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)
assert "." in version

with open("VERSION", "w", encoding="utf-8") as f:
    f.write("%s\n" % version)

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="syncable",
    version=version,
    description="Simple decorator for executing an asynchronous Python callable in a synchronous context.",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fullstackfarm/syncable",
    author="Fullstack Farm",
    author_email="aj@fullstackfarm.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    extras_require={
        "dev": ["twine>=6.1.0"],
    },
    python_requires=">=3.6"
)
