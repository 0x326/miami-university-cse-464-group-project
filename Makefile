all: report install lint test

install:
	pipenv install --dev

lint:
	@echo Recommended line length: 120-ish characters
	pipenv run pycodestyle src/ --max-line-length=140

lint-fix:
	@echo Recommended line length: 120-ish characters
	pipenv run autopep8 --in-place -r src/ --max-line-length=140

test:
	pipenv run python src/test*.py

report:
	cd writeups && latexmk -pdf *.tex
