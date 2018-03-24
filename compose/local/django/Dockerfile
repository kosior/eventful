FROM python:3.6
ENV PYTHONUNBUFFERED 1

ADD requirements /app/requirements/
RUN pip install -r /app/requirements/local.txt

ADD . /app
WORKDIR /app

ENV DOCKER_CONTAINER=1

EXPOSE 8000

