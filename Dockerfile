FROM python:3.9

RUN mkdir /opt/kinesis
WORKDIR /opt/kinesis

RUN apt-get update
RUN apt-get install -y openjdk-11-jdk
RUN apt-get install -y git
RUN apt-get install -y libev-dev

RUN python3 -m venv venv
RUN venv/bin/pip3 --no-cache-dir install --upgrade awscli
RUN venv/bin/pip3 install amazon_kclpy
RUN venv/bin/pip3 install pandas
RUN venv/bin/pip3 install boto3
RUN git clone https://github.com/awslabs/amazon-kinesis-client-python

WORKDIR /opt/kinesis/amazon-kinesis-client-python
RUN ../venv/bin/python setup.py download_jars
RUN ../venv/bin/python setup.py install

ADD examples /opt/kinesis/examples
ADD catalog /opt/kinesis/catalog
RUN ../venv/bin/pip3 install pytest
RUN mkdir /opt/kinesis/tests
ADD setup.py /opt/kinesis/setup.py
ADD test.sh /opt/kinesis/test.sh

ADD requirements.txt /opt/kinesis/requirements.txt

WORKDIR /opt/kinesis/

RUN venv/bin/pip3 install -r requirements.txt 
RUN venv/bin/python setup.py install
ENV PYTHON_PATH=.:/opt/kinesis/code:/opt/kinesis/tests:/opt/kinesis/examples

