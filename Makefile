.DEFAULT_GOAL := all
black = black --target-version py39 catalog
isort = isort --profile black catalog

.PHONY: init
init: 
	echo "Setting up virtual environment in venv/"
	python3 -m venv venv
	echo "Virtual environment complete."

.PHONY: format
format:
	$(isort)
	$(black)


.PHONY: lint
lint:
	flake8 --ignore=E203,F841,E501,E722,W503 catalog; exit 0
	$(isort) --check-only --df
	$(black) --check --diff

.PHONY: install
install: depends init
	pip install -r requirements.txt
	python setup.py install
	python setup.py clean

.PHONY: update
update: format lint
	pip freeze | grep -v catalog > requirements.txt
	git add setup.py docs bin catalog requirements.txt Makefile
	git commit --allow-empty -m "Updates"
	git push origin main
	python setup.py install
	git status


.PHONY: debug
debug: 
	python3 -m catalog.services.boot

.PHONY: update
up: 
	gunicorn --workers 4 --bind 0.0.0.0:5000 catalog.services.boot:app

.PHONY: clean
clean:
	python setup.py clean
	git status

.PHONY: all
all: format lint install
	git status