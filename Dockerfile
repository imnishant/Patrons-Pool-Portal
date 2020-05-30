FROM python:3.6-alpine

MAINTAINER Sankalp Saxena "sankalp.saxena.sta@gmail.com"

WORKDIR /home/Final-Year-Project
COPY . /home/Final-Year-Project

RUN python3 -m venv venv
RUN venv/bin/pip3 install -r requirements.txt


# environment variables required by flask
ENV FLASK_APP "main.py"
ENV FLASK_ENV "development"


RUN "source /venv/bin/activate"
#CMD . venv/bin/activate && pip3 install -r requirements.txt && flask db init && flask db migrate && flask db upgrade


CMD ["flask", "run"]


EXPOSE 5000


# mongodb still has to be added
# docker compose file still needs to be created