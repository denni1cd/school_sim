SHELL := /bin/bash

.PHONY: setup run simulate test

setup:
	python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

run:
	python main.py

simulate:
	python headless.py --ticks 300

test:
	pytest

