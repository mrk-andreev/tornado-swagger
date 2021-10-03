PACKAGE_CODE = tornado_swagger
OTHER_CODE = tests examples

format:
	autoflake --recursive --in-place --remove-all-unused-imports $(PACKAGE_CODE) $(OTHER_CODE)
	isort $(PACKAGE_CODE) $(OTHER_CODE)
	black --line-length=140 $(PACKAGE_CODE) $(OTHER_CODE)

lint:
	flake8 --jobs 1 --statistics --show-source $(PACKAGE_CODE)
	pylint --jobs 1 --rcfile=setup.cfg $(PACKAGE_CODE)
	black --line-length=140 --check $(PACKAGE_CODE) $(OTHER_CODE)

test:
	python -m pytest .
