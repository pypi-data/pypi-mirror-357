#! /bin/bash

# Lint the code with ruff
ruff check --fix .

# Lint the code with mypy
mypy .
