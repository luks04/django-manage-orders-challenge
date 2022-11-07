FROM python:3.10-buster

WORKDIR /usr/src/app

COPY ./app .
COPY ./requirements.txt /usr/src/app

# Install python requirements
RUN pip install -r requirements.txt

EXPOSE 8080

CMD python manage.py runserver 0.0.0.0:8080