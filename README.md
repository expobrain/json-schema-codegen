[![Build Status](https://travis-ci.org/expobrain/json-schema-codegen.svg?branch=master)](https://travis-ci.org/expobrain/json-schema-codegen)

# json-schema-codegen

Generate code from JSON schema files.

# Table of contents

- [Introduction](#introduction)
- [Currently supported languages](#currently-supported-languages)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Code generation](#code-generation)
  - [Python3](#python-3)
  - [Python3+Marshmallow](#python-3marshmallow)
  - [JavaScript+Flow and Flow](#javascriptflow-and-flow)
- [Contribute](#contribute)

# Introduction

This is a command line tool to take a [json-schema](http://json-schema.org/) file and generate code automatically.

For instance this `json-schema` definition:

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "title": "Test",
  "type": "object",
  "properties": {
    "id": { "type": "integer" }
  }
}
```

will generate this Python code:

```python
class Test(object):
    def __init__(self, data=None):
        data = data or {}

        self.id = data.get("id")
```

or this JavaScript+Flow code:

```javascript
export class Test {
  id: ?number;

  constructor(data: Object = {}) {
    this.id = data.id;
  }
}
```

Currently this tool generates code for Python and JavaScript with [Flow](https://flow.org/) annotations but it can be extended to generate code for any language.

The code generation is divided in two stages:

1.  generate the [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) for the target language from the `json-schema` file
1.  convert the AST into the target language

This allows the tool to be language agnostic, that is it just needs to generate the AST in JSON format for the target language and then a language specific tool will convert this AST into proper code.

# Currently supported languages

List of currently supported languages:

- Python 3.7+
- JavaScript ES7+ with Flow annotations
- pure Flow annotations

# Requirements

- Python 3.6 / 3.7
- Node v12

# Installation

Until this [pull request](https://github.com/pypa/setuptools/pull/1389) in [`setuptools`](https://pypi.org/project/setuptools/) is fixed, the only way to install `json-schema-codegen` is to clone the repo:

```shell
git clone https://github.com/expobrain/json-schema-codegen.git
```

# Usage

```shell
usage: json_codegen.py [-h] [--prefix PREFIX] [--language LANGUAGE]
                       [--output OUTPUT]
                       schema

positional arguments:
  schema                Definition of the PRD as JSON schema

optional arguments:
  -h, --help            show this help message and exit
  --prefix PREFIX, -p PREFIX
                        Optional prefix for generated classes
  --language LANGUAGE, -l LANGUAGE
                        Output language. Default is python
  --output OUTPUT, -o OUTPUT
                        Output filename for the generated code
```

# Code generation

## Python 3

The egenerator of pure Python 3 compatible code:

```shell
json_codegen --language python3 --output <output_py_file> <json-schema>
```

## Python 3+Marshmallow

The generation of Python 3's code with [Marshmallow](https://marshmallow.readthedocs.io/en/2.x-line/) support is integrated into the tool so it needs just a single invocation:

```shell
json_codegen --language python3+marshmallow --output <output_py_file> <json-schema>
```

## JavaScript+Flow and Flow

Generating JavaScript+Flow and Flow code involves two steps, generating the AST:

```shell
json_codegen --language [javascript+flow|flow] --output <output_ast_json> <json-schema>
```

and generating the code from the AST:

```shell
bin/ast_to_js <output_ast_json> <output_js_file>
```
