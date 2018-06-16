from setuptools import setup, find_packages


setup(
    name="json-schema-codegen",
    version="0.1",
    keywords="pytohn javascript json-schema codegen",
    author="Daniele Esposti",
    author_email="daniele.esposti@gmail.com",
    url="https://github.com/expobrain/json-schema-codegen",
    packages=find_packages(),
    entry_points={"console_scripts": ["json_codegen = json_codegen:main"]},
    python_requires="<=3",
    license="MIT",
    install_requires=["astor==0.6.2", "pathlib2==2.3.0"],
    # Disable because of https://github.com/pypa/setuptools/issues/761
    # scripts=["bin/ast_to_js"],
)
