# Variables
PYTHON_SCRIPT=./src/main.py
REQUIREMENTS=requirements.txt

# Install dependencies
.PHONY: install
install:
	pip install -r $(REQUIREMENTS)

# Run the application
.PHONY: run
run:
	python3 $(PYTHON_SCRIPT)
