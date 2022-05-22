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


## Configuration

The basic configuration is done in the .env file, which defaults to

```
AWS_DIR=~/.aws
AVAIL_STREAM_NAME=content-catalog-avail
ALID_STREAM_NAME=content-catalog-alid
SERVICE_DIR=./amazon-kinesis-client-python/samples
PYTHON_PATH=.:opt/kinesis/code:/opt/kinesis/tests:/opt/kinesis/examples
PARTITION_KEY=test-key
GLUE_REGISTRY=default-registry
ALID_SCHEMA=/opt/kinesis/schemas/alid.json
AVAIL_SCHEMA=/opt/kinesis/schemas/avail.json
```

*AWS_DIR* is your .aws config directory containing your credentials

*AVAIL_STREAM_NAME* is the name of the AVAIL kinesis stream

*ALID_STREAM_NAME* is the name of the ALID kinesis stream

*SERVICE_DIR* is where your kinesis python client code resides (aka your service) on your host computer. This is then mounted as a volume by compose.

*PYTHON_PATH* should not have to be changed, but you can add to it if necessary

*PARTITION_KEY* Kinesis stream partition key.

*GLUE-REGISTRY* Name of AWS Glue registry where message schemas will be posted

*ALID_SCHEMA* The json-schema file for ALID messages

*AVAIL_SCHEMA* The json-schema file for AVAIL messages

## Test

The unit test for it (also from AWS) is in `tests` directory.

```
$ docker compose up test
```

## Development Setup

To start, you will need to set a couple environment variables to override the .env which will set paths within the container.

```
$ export ALID_SCHEMA=./schemas/alid.json
$ export AVAIL_SCHEMA=schemas/avail.json
```
Then you need to make the virtual environment for development
```
$ make init
...
$ source venv/bin/activate
```

## Running the Endpoint

The kinesis microservice allows Content Catalog to send messages to Kinesis (or future messaging hub of choice) in a standard, client-agnostic manner, for example, using basic http requests.

```
$ make debug
```

This will launch the flask endpoint in debug mode. 

NOTE: During startup, you may see some exceptions logged to the console such as 
```
botocore.errorfactory.ResourceInUseException: An error occurred (ResourceInUseException) when calling the CreateStream operation: Stream content-catalog-alid under account 898726884252 already exists.
```
This is expected and is visible for information purposes. Since the schema it is trying to create is already created, it is logging this fact.

## OpenAPI (formerly Swagger)

After the startup completes you can visit http://localhost:5000 to reach the OpenAPI UI

You can use the sample/dummy messages located in `./schemas/messages/` to paste into the POST endpoint calls, just be sure you use the `samele-alid.json` for the ALID API endpoint and the `sample-avail.json` for the AVAIL API endpoint.
