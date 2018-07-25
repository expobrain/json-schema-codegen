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
  - [Python](#python)
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

- Python 2.7
- JavaScript ES7+ with Flow annotations
- pure Flow annotations

# Requirements

- Python 2.7
- Node v8.4+

# Installation

Until this [pull request](https://github.com/pypa/setuptools/pull/1389) in [`setuptools`](https://pypi.org/project/setuptools/) is fixed, the only way to install `json-schema-codegen` is to clone the repo:

```
git clone https://github.com/expobrain/json-schema-codegen.git
```

# Usage

```
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

## Python

The generation of Python's code is integrated into the tool so it needs just a single invocation:

```
json-codegen.py --language python --output <output_py_file> <json-schema>
```

## JavaScript+Flow and Flow

Generating JavaScript+Flow and Flow code involves two steps, generating the AST:

```
json-codegen.py --language [javascript|flow] --output <output_ast_json> <json-schema>
```

and generating the code from the AST:

```
bin/ast_to_js <output_ast_json> <output_js_file>
```

# Contribute

Clone the repository, install packages and setup git hooks:

```
git clone https://github.com/expobrain/json-schema-codegen
pip install -r requirements_dev.txt
yarn install
git config core.hooksPath .githooks
```
