import pytest

from json_codegen import cli
from json_codegen.core import BaseGenerator


def test_langages():
    languages = set(cli.LANGUAGES.keys())
    expected = {"python3", "python3+marshmallow", "javascript+flow", "flow"}

    assert languages == expected


@pytest.mark.parametrize("language", cli.LANGUAGES.keys())
def test_get_generator(language):
    generator = cli.get_generator(language)

    assert issubclass(generator, BaseGenerator)
