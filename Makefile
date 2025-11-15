SHELL := /bin/bash

.PHONY: setup run simulate demo test clean-logs

setup:
	python -m venv .venv
	python -m pip install -r requirements.txt

run:
	python -m school_sim.main

simulate:
	python -m school_sim.headless --ticks 300

demo:
	@echo ">>> Headless snapshot (120 ticks)"
	python -m school_sim.headless --ticks 120 --log-path school_sim/runtime/logs/demo_sim_log.txt
	@echo "Log written to school_sim/runtime/logs/demo_sim_log.txt"
	@echo ">>> Interactive slice (auto-stops after 12 loops)"
	SCHOOL_SIM_MAX_LOOPS=12 python -m school_sim.main

test:
	python -m pytest -q school_sim/tests

clean-logs:
	rm -f school_sim/runtime/logs/*.txt

