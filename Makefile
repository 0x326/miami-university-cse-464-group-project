all: report install lint test

install:
	pipenv install --dev

lint:
	@echo Max line length: 120-ish characters
	pipenv run pycodestyle src/ --max-line-length=140

lint-fix:
	@echo Max line length: 120-ish characters
	pipenv run autopep8 --in-place -r src/ --max-line-length=140

test:
	cd src/ && pipenv run pytest
	cd src/ && pipenv run python test*.py

report:
	cd writeups && latexmk -pdf *.tex
