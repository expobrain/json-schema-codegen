.SILENT: mypy

mypy:
	poetry run mypy .

install:
	poetry install --sync
