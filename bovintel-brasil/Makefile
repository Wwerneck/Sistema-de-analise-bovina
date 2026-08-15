.PHONY: setup extract transform validate analyze forecast dashboard all

setup:
	python -m pip install -e ".[dev]"

extract:
	python -m bovintel.cli extract

transform:
	python -m bovintel.cli transform

validate:
	python -m bovintel.cli validate
	pytest -q

analyze:
	python -m bovintel.cli analyze

forecast:
	python -m bovintel.cli forecast

dashboard:
	python -m bovintel.cli dashboard

all: extract transform validate analyze forecast dashboard
