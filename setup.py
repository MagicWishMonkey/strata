import os
from setuptools import setup
from setuptools import find_packages

readme, dependencies = "", []
with open("docs%srequirements.txt" % os.sep) as f:
    dependencies = f.read().splitlines()

with open("docs%sreadme.txt" % os.sep) as f:
    readme = f.read()

setup(
    name = "strata",
    version = "1.0",
    author = "Ron Rodenberg",
    author_email = "rodenberg@gmail.com",
    description = "This is the strata application framework.",
    license = "MIT",
    packages=find_packages(),
    long_description=readme,
    install_requires=dependencies
)