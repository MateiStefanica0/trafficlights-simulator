# Define the Python interpreter
PYTHON := python3

# Define the pip command
PIP := pip3

# Define the requirements file
REQUIREMENTS := requirements.txt

# Define the main script
MAIN_SCRIPT := ./src/main.py

# Install dependencies
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)

# Run the main script
run: install
	$(PYTHON) $(MAIN_SCRIPT)

# Clean up any generated files (optional)
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

.PHONY: install run clean