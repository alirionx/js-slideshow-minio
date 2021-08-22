FROM ubuntu:focal

RUN apt update && apt install -y \
  python3 \
  python3-pip 

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY . /data
RUN pip3 install waitress

WORKDIR /data
EXPOSE 5000

CMD waitress-serve --port=5000 "main:app" 