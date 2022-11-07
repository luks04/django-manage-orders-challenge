FROM python:3.10-buster

RUN apt update
RUN apt-get install cron -y
RUN alias py=python

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY ./app .
COPY ./requirements.txt /usr/src/app

# Install python requirements
RUN pip install -r requirements.txt

# Django-crontab logfile
RUN mkdir /cron
RUN touch /cron/django_cron.log

RUN python manage.py makemigrations core
RUN python manage.py migrate core
RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8080

CMD service cron start && python manage.py crontab add && python manage.py runserver 0.0.0.0:8080