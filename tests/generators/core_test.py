from pathlib import Path

import pytest

from generators.core import BaseGenerator, GeneratorNotFoundException, load_external_generator


fixture_dir = Path(__file__).parent / "fixtures"


def test_load_external_generator():
    filename = fixture_dir / "custom_generator.py"

    generator = load_external_generator(filename)

    assert issubclass(generator, BaseGenerator)


def test_load_external_generator_class_not_found():
    filename = fixture_dir / "class_not_found_generator.py"

    with pytest.raises(GeneratorNotFoundException):
        load_external_generator(filename)


def test_load_external_generator_file_not_found():
    filename = fixture_dir / "file_not_found_generator.py"

    with pytest.raises(FileNotFoundError):
        load_external_generator(filename)
