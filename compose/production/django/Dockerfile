FROM python:3.6
ENV PYTHONUNBUFFERED 1

ADD requirements /app/requirements/
RUN pip install -r /app/requirements/production.txt

ADD . /app
WORKDIR /app

ENV DOCKER_CONTAINER=1

COPY ./compose/production/django/prod_run.sh /prod_run.sh
RUN chmod +x /prod_run.sh


