SHELL := /bin/bash

.PHONY: setup run simulate test

setup:
	python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

run:
	python -m game.play

simulate:
	python -m game.app

test:
	pytest -v -q

