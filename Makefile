all: report install lint test

install:
	pipenv install --dev

lint:
	pipenv run pycodestyle src/ --max-line-length=120

lint-fix:
	pipenv run autopep8 --in-place -r src/ --max-line-length=120

test:
	pipenv run python src/test*.py

report:
	cd writeups && latexmk -pdf *.tex
