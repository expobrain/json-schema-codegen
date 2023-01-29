#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
import sys

sys.path.append((Path(__file__).parent.resolve() / "..").as_posix())

from json_codegen import generators
from json_codegen.core import load_schema, load_external_generator


LANGUAGES = {
    "python3": generators.Python3Generator,
    "python3+marshmallow": generators.Python3MarshmallowGenerator,
    "javascript+flow": generators.JavaScriptFlowGenerator,
    "flow": generators.FlowGenerator,
}


def get_generator(language):
    try:
        return LANGUAGES[language]
    except KeyError:
        raise ValueError("Language {} not supported".format(language))


def main():
    # Validating parameters
    parser = ArgumentParser(description="Generates code from a JSON-schema definition")
    parser.add_argument("--prefix", "-p", help="Optional prefix for generated classes")
    parser.add_argument(
        "--output", "-o", help="Output filename for the generated code. Default is stdout"
    )
    parser.add_argument(
        "--generator",
        "-g",
        help=(
            "Path to an external custom code generator. "
            "When used the option --language will be ignored."
        ),
    )
    parser.add_argument("schema", help="Definition of the PRD as JSON schema")
    parser.add_argument(
        "--language",
        "-l",
        choices=LANGUAGES,
        help=(
            "Output language. "
            "This option will be ignored if the --generator option is used. "
            "Default is python3"
        ),
    )

    args = parser.parse_args()

    # Load schema
    with open(args.schema) as f:
        schema = load_schema(f.read())

    # Generate code
    if args.generator:
        generator = load_external_generator(args.generator)
    else:
        generator = get_generator(args.language)

    code = generator(schema, prefix=args.prefix).generate().as_code()

    # Output code
    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
    else:
        sys.stdout.write(code)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
