FROM python:3.9

RUN mkdir /opt/kinesis
WORKDIR /opt/kinesis

RUN apt-get update
RUN apt-get install -y openjdk-11-jdk

RUN python3 -m venv venv
RUN venv/bin/pip3 --no-cache-dir install --upgrade awscli
RUN venv/bin/pip3 install amazon_kclpy
RUN venv/bin/pip3 install pandas
RUN venv/bin/pip3 install boto3
