#!/usr/bin/env python3

import ast
import sys

import astor


print(astor.dump_tree(ast.parse(sys.argv[1]).body))
