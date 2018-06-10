all:

PYTHON := venv/bin/python -Werror \
	-Wignore:'The imp module'::: \
	-Wignore:'Importing from django.core.urlresolvers'::: \
	-Wignore:'The `convert` argument is deprecated'

flake:
	venv/bin/flake8

pipcheck:
	venv/bin/pip check --quiet

test-server:
	$(PYTHON) manage.py check
	$(PYTHON) -m pytest

test: test-server

check: flake pipcheck test

run:
	./manage.py runserver --nostatic

init:
	python3.5 -m venv venv
	venv/bin/pip install --require-hashes -r requirements.txt
	venv/bin/pip install -r requirements-dev.txt

makemessages:
	$(PYTHON) manage.py makemessages --ignore=venv --no-location

compilemessage:
	cd locale && ../$(PYTHON) ../manage.py compilemessages

makemigrations:
	$(PYTHON) manage.py makemigrations

migrate:
	$(PYTHON) manage.py migrate
