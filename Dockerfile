FROM python:3.9

RUN mkdir /opt/kinesis
WORKDIR /opt/kinesis

RUN apt-get update
RUN apt-get install -y openjdk-11-jdk
RUN apt-get install -y git

RUN python3 -m venv venv
RUN venv/bin/pip3 --no-cache-dir install --upgrade awscli
RUN venv/bin/pip3 install amazon_kclpy
RUN venv/bin/pip3 install pandas
RUN venv/bin/pip3 install boto3
RUN git clone https://github.com/awslabs/amazon-kinesis-client-python

WORKDIR /opt/kinesis/amazon-kinesis-client-python
RUN ../venv/bin/python setup.py download_jars
RUN ../venv/bin/python setup.py install

ADD test.sh /opt/kinesis/test.sh
ENV PYTHON_PATH=/opt/kinesis/code

WORKDIR /opt/kinesis
