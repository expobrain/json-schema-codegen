import setuptools
from pkg_resources import parse_version

SETUPTOOLS_MIN_VER = "40.1.0"

if parse_version(setuptools.__version__) < parse_version(SETUPTOOLS_MIN_VER):
    raise RuntimeError("setuptools minimum required version: %s" % SETUPTOOLS_MIN_VER)

from setuptools import setup, find_packages

setup(
    name="json_codegen",
    version="0.2.1",
    keywords="python javascript json-schema codegen",
    author="Daniele Esposti",
    author_email="daniele.esposti@gmail.com",
    url="https://github.com/expobrain/json-schema-codegen",
    packages=find_packages(),
    entry_points={"console_scripts": ["json_codegen = json_codegen.cli:main"]},
    python_requires=">=3",
    license="MIT",
    install_requires=["astor>=0.7.1", "setuptools>={}".format(SETUPTOOLS_MIN_VER)],
    scripts=["bin/ast_to_js"],
)
