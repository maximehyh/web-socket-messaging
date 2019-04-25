FROM python:3.6

RUN apt-get update && \
        apt-get install -y \
        build-essential

COPY . /app/
WORKDIR /app/

RUN pip3 install -r requirements.txt