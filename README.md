# kinesis-python-container
A python-based AWS Kinesis docker container

## Overview

This docker bundles all the dependencies to run Kinesis services from python. Your service code remains on your host computer and is mounted as a volume by the container. This makes it easy to deploy the container to various environments and swap out the python service code easily (for different services for example).

Additionally, it mounts your .aws config directory as a volume as well. This is configured in the .env file

## Install

Step 1

```
$ git clone https://github.com/awslabs/amazon-kinesis-client-python
```

Step 2

```
$ docker-compose build kinesis
```

Step 3

```
$ cp sample.env .env
```

## Example

To run the amazon kinesis example code

```
$ docker-compose up kinesis
```

If everything went well, you should see

```
Starting kinesis ... done
Attaching to kinesis
kinesis    | Connecting to stream: words in us-east-1
kinesis    | Put word: cat into stream: words
kinesis    | Put word: dog into stream: words
kinesis    | Put word: bird into stream: words
kinesis    | Put word: lobster into stream: words
kinesis exited with code 0
```

### AWS Example

In the `examples` directory is a kinesis stream example from AWS. The unit test for it (also from AWS) is in `tests` directory.
To run this

```
$ 


```

## Configuration

The basic configuration is done in the .env file, which defaults to

```
AWS_DIR=~/.aws
KINESIS_ENDPOINT=http://kinesis.[namespace].svc
SERVICE_DIR=./amazon-kinesis-client-python/samples
```

AWS_DIR is your .aws config directory containing your credentials
KINESIS_ENDPOINT is not currently used, but will soon. TBD
SERVICE_DIR is where your kineis python client code resides (aka your service) on your host computer. This is then mounted as a volume by compose.