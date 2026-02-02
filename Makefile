VENV_DIR := .venv

.PHONY: install
install:
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip

.PHONY: run
run: $(VENV_DIR)
	$(VENV_DIR)/bin/python merit_calculator.py

.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf .pytest_cache

.PHONY: reinstall
reinstall: clean install
