FROM python:3.5.2
ENV PYTHONUNBUFFERED 1
WORKDIR /docker_django
ADD . /docker_django/
CMD python3.5 -m venv venv
CMD docker_django/venv/bin/pip install -r requirements.txt
# Django service
XPOSE 8000
