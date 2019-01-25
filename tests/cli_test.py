import pytest

from json_codegen import cli
from json_codegen.core import BaseGenerator


def test_langages():
    languages = set(cli.LANGUAGES.keys())
    expected = set(["python2", "python3", "javascript+flow", "flow"])

    assert languages == expected


@pytest.mark.parametrize("language", cli.LANGUAGES.keys())
def test_get_generator(language):
    generator = cli.get_generator(language)

    assert issubclass(generator, BaseGenerator)
