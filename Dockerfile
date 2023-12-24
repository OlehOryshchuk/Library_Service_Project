FROM python:3.11.1-alpine

LABEL maintainer="olehoryshshuk@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR library_service_api/

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /static

RUN adduser \
        --disabled-password \
        --no-create-home \
        library_service_user

RUN chown -R library_service_user:library_service_user /static/

RUN chmod -R 755 /static/

USER library_service_user
