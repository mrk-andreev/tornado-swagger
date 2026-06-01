PACKAGE_CODE = tornado_swagger
OTHER_CODE = tests examples
PYTHON ?= python

.PHONY: format lint test test-matrix test-in-docker

format:
	ruff check --fix $(PACKAGE_CODE) $(OTHER_CODE)
	black --line-length=140 $(PACKAGE_CODE) $(OTHER_CODE)

lint:
	ruff check $(PACKAGE_CODE) $(OTHER_CODE)
	black --line-length=140 --check $(PACKAGE_CODE) $(OTHER_CODE)

test:
	$(PYTHON) -m pytest .

test-matrix:
	$(PYTHON) -m tox


test-in-docker:
	bash run_tests_in_docker.bash
