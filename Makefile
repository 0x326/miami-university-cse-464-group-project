all: report install lint test

install:
	pipenv install --dev

lint:
	pipenv run pycodestyle src/ --max-line-length=120

test:
	pipenv run python src/test*.py

report:
	cd writeups && latexmk -pdf *.tex
