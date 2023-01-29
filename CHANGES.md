# Changelog

## v0.6.0

### Backward incompatible changes

- dropped generatino of Python 2 code

## v0.4.6

### Trivial/internal changes

- In the generated code for Python 3 classes don't inherit from `object`
- Migrated to Poetry as package management

## v0.4.5

### Bug fixes

- [#27](https://github.com/expobrain/json-schema-codegen/pull/27) Fixes generation of proper nullable scalars and objects

## v0.4.4

### Bug fixes

- [#30](https://github.com/expobrain/json-schema-codegen/pull/30) Nested objects had an ahrdoced name instead of the reference's name

## v0.4.3.1

### Bug fixes

- [#28](https://github.com/expobrain/json-schema-codegen/pull/28) Value is not coerced to object

## v0.4.2

### Bug fixes

- [#26](https://github.com/expobrain/json-schema-codegen/pull/26) Required fields were not honored in Python generators

## v0.4.1

### Bug fixes

- [#25](https://github.com/expobrain/json-schema-codegen/pull/25) Fixed error when object type without default value

## v0.4.0

### Breaking changes

- [#23](https://github.com/expobrain/json-schema-codegen/pull/23) Use list validation in the schemas to generate lists instead of generating them from a tuple validation. See https://json-schema.org/understanding-json-schema/reference/array.html#items.

### New features

- [#24](https://github.com/expobrain/json-schema-codegen/pull/24) Added generation of pure Python 3 compatible code

### Trivial/internal changes

- [#21](https://github.com/expobrain/json-schema-codegen/pull/21) Fixed anchors in README
- [#22](https://github.com/expobrain/json-schema-codegen/pull/22) Various internal improvements and fixes

## v0.3.0

### Backward imcompatible changes

- [#20](https://github.com/expobrain/json-schema-codegen/pull/20) Renamed `python3` code generator into `python3+marshmallow`

### Trivial/internal changes

- [#19](https://github.com/expobrain/json-schema-codegen/pull/19) Removed `pathlib2` as a dependency
