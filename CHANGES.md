# Changelog

## Unreleased

### Breaking changes

- [#23](https://github.com/expobrain/json-schema-codegen/pull/23) Use list validation in the schemas to generate lists instead of generating them from a tuple validation. See https://json-schema.org/understanding-json-schema/reference/array.html#items.

### Trivial/internal changes

- [#21](https://github.com/expobrain/json-schema-codegen/pull/21) Fixed anchors in README
- [#22](https://github.com/expobrain/json-schema-codegen/pull/22) Various internal improvements and fixes

## v0.3.0

### Backward imcompatible changes

- [#20](https://github.com/expobrain/json-schema-codegen/pull/20) Renamed `python3` code generator into `python3+marshmallow`

### Trivial/internal changes

- [#19](https://github.com/expobrain/json-schema-codegen/pull/19) Removed `pathlib2` as a dependency