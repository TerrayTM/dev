import re

from setuptools import setup

with open("dev/version.py", "r", encoding="utf-8") as file:
    version = file.readline()

match = re.match(r"^__version__ = \"([\d\.]+)\"$", version)

if match:
    __version__ = match.group(1)
else:
    raise RuntimeError()

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="dev-star",
    packages=["dev"],
    version=__version__,
    description="Dev tools CLI for performing common development tasks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Terry Zheng",
    author_email="contact@terrytm.com",
    maintainer="Terry Zheng",
    maintainer_email="contact@terrytm.com",
    url="https://dev.terrytm.com",
    python_requires=">=3.8",
    keywords="developer tools",
    license="Apache 2.0",
    zip_safe=False,
    install_requires=[],
    project_urls={
        "Bug Reports": "https://dev.terrytm.com/issues",
        "Documentation": "https://dev.terrytm.com",
        "Source Code": "https://github.com/TerrayTM/dev",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={"console_scripts": ["dev = dev.main:main"]},
)
