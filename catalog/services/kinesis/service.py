
import json
import os
import datetime
import boto3
import subprocess
from ..logging import logging
from pathlib import Path
from botocore.exceptions import ClientError
from flask_restx import Namespace, Resource, fields
from .fixtures.common import fixture_make_stubber
from jsonschema import (
    Draft4Validator,
    FormatChecker,
)

api = Namespace("kinesis", "Kinesis service for Content Catalog", validate=True)

validators = {}
schemas = {}
models = {}

def update_schema(schema, registry):
    """ Update a schema to glue schema registry (create if not exists) """
    with open(schema,'r') as avail:
        name = Path(avail.name).stem
        cmd = f"/home/darren/git/kinesis-python-container/venv/bin/aws glue create-schema  --schema-name {name} --data-format JSON --schema-definition file://{schema} --compatibility FORWARD"
        logging.info(cmd)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        logging.info(result.stdout)

        cmd = f"aws glue register-schema-version --schema-id SchemaName={name},RegistryName=default-registry --schema-definition file://{schema} "
        logging.info(cmd)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        logging.info(result.stdout)

        the_schema = json.loads(avail.read())

        the_model = api.schema_model(name, the_schema)

        the_validator = Draft4Validator(the_schema, format_checker=FormatChecker())

        validators[schema] = the_validator
        schemas[schema] = the_schema
        models[schema] = the_model

update_schema(os.environ['AVAIL_SCHEMA'], 'default-registry')
update_schema(os.environ['ALID_SCHEMA'], 'default-registry')

session = boto3.Session()   # Credentials are picked up from AWS_DIR env var, which points
                            # to mounted directory

glue_client = session.client('glue')

logging.debug("PARTITION KEY %s",os.environ['PARTITION_KEY'])
logging.debug("GLUE CLIENT %s",glue_client)

# Parts used from AWS example here: 
# https://docs.aws.amazon.com/code-samples/latest/catalog/python-kinesis-streams-kinesis_stream.py.html
class CatalogKinesisStream:

    def __init__(self, kinesis_client):
        self.kinesis_client = kinesis_client
        self.stream_exists_waiter = kinesis_client.get_waiter('stream_exists')

    def describe(self, name):
        try:
            response = self.kinesis_client.describe_stream(StreamName=name)
            self.name = name
            self.details = response['StreamDescription']
            logging.info("Got stream %s.", name)
        except ClientError:
            logging.exception("Couldn't get %s.", name)
            raise
        else:
            return self.details

    def get_records(self, max_records):
        try:
            response = self.kinesis_client.get_shard_iterator(
                StreamName=self.name, ShardId=self.details['Shards'][0]['ShardId'],
                ShardIteratorType='LATEST')
            shard_iter = response['ShardIterator']
            record_count = 0
            while record_count < max_records:
                response = self.kinesis_client.get_records(
                    ShardIterator=shard_iter, Limit=10)
                shard_iter = response['NextShardIterator']
                records = response['Records']
                logging.info("Got %s records.", len(records))
                record_count += len(records)
                yield records
        except ClientError:
            logging.exception("Couldn't get records from stream %s.", self.name)
            raise

    def put_record(self, data, partition_key):
        try:
            response = self.kinesis_client.put_record(
                StreamName=self.name,
                Data=json.dumps(data),
                PartitionKey=partition_key)
            logging.info("Put record in stream %s.", self.name)
        except ClientError:
            logging.exception("Couldn't put record in stream %s.", self.name)
            raise
        else:
            return response

    def create(self, name, wait_until_exists=True):
        try:
            self.kinesis_client.create_stream(StreamName=name, ShardCount=1)
            self.name = name
            logging.info("Created stream %s.", name)
            if wait_until_exists:
                logging.info("Waiting until exists.")
                self.stream_exists_waiter.wait(StreamName=name)
                self.describe(name)
        except ClientError:
            logging.exception("Couldn't create stream %s.", name)
            raise

kinesis = CatalogKinesisStream(boto3.client('kinesis'))

@api.route("/alid")
class CatalogAlidKinesisService(Resource):

    def get(self):
        records = kinesis.get_records(10)
        return json.dumps(records)

    @api.expect(models[os.environ['ALID_SCHEMA']], validate=True)
    def post(self):
        assert validators[os.environ['ALID_SCHEMA']].is_valid(api.payload) is True
        date = datetime.datetime.now()
        timestamp = date.timestamp()
        response = kinesis.put_record(api.payload,'alid')

        return {"status": "posted", "schema":"alid", "timestamp":timestamp, "date":str(date), "response":json.dumps(response)}

@api.route("/avail")
class CatalogAvailKinesisService(Resource):

    def get(self):
        return {"status": "ok"}

    @api.expect(models[os.environ['AVAIL_SCHEMA']], validate=True)
    def post(self):
        assert validators[os.environ['AVAIL_SCHEMA']].is_valid(api.payload) is True
        date = datetime.datetime.now()
        timestamp = date.timestamp()
        response = kinesis.put_record(api.payload,'avail')

        return {"status": "posted", "schema":"avail", "timestamp":timestamp, "date":str(date), "response":json.dumps(response)}