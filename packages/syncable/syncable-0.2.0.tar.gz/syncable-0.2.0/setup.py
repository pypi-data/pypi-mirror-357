from setuptools import setup, find_packages
import subprocess
import os

version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)

if "-" in version:
    # when not on tag, git describe outputs: "1.3.3-22-gdf81228"
    # pip has gotten strict with version numbers
    # so change it to: "1.3.3+22.git.gdf81228"
    # See: https://peps.python.org/pep-0440/#local-version-segments
    v, i, s = version.split("-")
    version = v + "+" + i + ".git." + s

assert "-" not in version
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
    install_requires=["anyio>=4.0"],
    extras_require={
        "dev": ["twine>=6.1.0"],
    },
    python_requires=">=3.6"
)
