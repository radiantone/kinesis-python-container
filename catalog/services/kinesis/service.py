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

from dotenv import load_dotenv
load_dotenv()

api = Namespace("kinesis", "Kinesis service for Content Catalog", validate=True)

validators = {}
schemas = {}
models = {}

class DatetimeEncoder(json.JSONEncoder):
    # REF: https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def update_schema(schema, registry):
    """ Update a schema to glue schema registry (create if not exists) """
    with open(schema,'r') as schema_file:
        name = Path(schema_file.name).stem
        cli = os.environ['AWS_CLI']
        registry = os.environ['GLUE_REGISTRY']

        cmd = f"{cli} glue create-schema  --schema-name {name} --data-format JSON --schema-definition file://{schema} --compatibility FORWARD"
        logging.info(cmd)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        logging.info(result.stdout)

        cmd = f"{cli} glue register-schema-version --schema-id SchemaName={name},RegistryName={registry} --schema-definition file://{schema} "
        logging.info(cmd)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        logging.info(result.stdout)

        the_schema = json.loads(schema_file.read())

        the_model = api.schema_model(name, the_schema)

        the_validator = Draft4Validator(the_schema, format_checker=FormatChecker())

        validators[schema] = the_validator
        schemas[schema] = the_schema
        models[schema] = the_model


update_schema(os.environ['AVAIL_SCHEMA'], os.environ['GLUE_REGISTRY'])
update_schema(os.environ['ALID_SCHEMA'], os.environ['GLUE_REGISTRY'])

logging.debug("GLUE_REGISTRY %s, PARTITION KEY %s",os.environ['GLUE_REGISTRY'], os.environ['PARTITION_KEY'])

# Parts used from AWS example here: 
# https://docs.aws.amazon.com/code-samples/latest/catalog/python-kinesis-streams-kinesis_stream.py.html
class CatalogKinesisStream:

    def __init__(self, kinesis_client):
        self.kinesis_client = kinesis_client
        self.stream_exists_waiter = kinesis_client.get_waiter('stream_exists')
        self.name = None
        self.details = {}

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
            logging.info("get_records: %s %s",self.details['Shards'][0]['ShardId'], self.name)
            response = self.kinesis_client.get_shard_iterator(
                StreamName=self.name, ShardId=self.details['Shards'][0]['ShardId'],
                ShardIteratorType='TRIM_HORIZON')
            shard_iter = response['ShardIterator']
            logging.info("get_records: get_shard_iterator: %s",response)
            response = self.kinesis_client.get_records(
                ShardIterator=shard_iter, Limit=max_records)
            logging.info("get_records: get_records: %s",response)
            return response
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
            self.name = name
            self.kinesis_client.create_stream(StreamName=name, ShardCount=1)
            logging.info("Created stream %s.", name)
            if wait_until_exists:
                logging.info("Waiting until exists.")
                self.stream_exists_waiter.wait(StreamName=name)
                self.describe(name)
        except ClientError:
            logging.exception("Couldn't create stream %s.", name)
            raise


@api.route("/alid")
class CatalogAlidKinesisService(Resource):
    """ Catalog alid kinesis stream endpoint """

    def __init__(self, arg):
        super(CatalogAlidKinesisService, self).__init__()
        print("ARG",arg)
        self.alid_stream = CatalogKinesisStream(boto3.client('kinesis'))


        logging.debug("Creating alid kinesis stream...")
        try:
            self.alid_stream.create(os.environ['ALID_STREAM_NAME'])
            logging.debug("Alid kinesis stream created...")
        except Exception as ex:
            logging.warning("Kinesis stream %s already exists.",os.environ['ALID_STREAM_NAME'])
        finally:
            self.alid_stream.describe(os.environ['ALID_STREAM_NAME'])

    def get(self):
        records = self.alid_stream.get_records(10)

        return json.dumps(records, cls=DatetimeEncoder) #json.dumps([json.dumps(record, cls=DatetimeEncoder) for record in records])

    @api.expect(models[os.environ['ALID_SCHEMA']], validate=True)
    def post(self):

        return self.put_message(api.payload)

    def put_message(self, message):
        print(message)
        assert validators[os.environ['ALID_SCHEMA']].is_valid(message) is True
        date = datetime.datetime.now()
        timestamp = date.timestamp()
        response = self.alid_stream.put_record(message,'alid')

        return {"status": "posted", "schema":"alid", "timestamp":timestamp, "date":str(date), "response":json.dumps(response)}

@api.route("/avail")
class CatalogAvailKinesisService(Resource):
    """ Catalog avail kinesis stream endpoint """

    def __init__(self):
        super(CatalogAvailKinesisService, self).__init__()
        self.avail_stream = CatalogKinesisStream(boto3.client('kinesis'))


        logging.debug("Creating availkinesis stream...")
        try:
            self.avail_stream.create(os.environ['AVAIL_STREAM_NAME'])
            logging.debug("Avail kinesis stream created...")
        except Exception as ex:
            logging.warning("Kinesis stream %s already exists.",os.environ['AVAIL_STREAM_NAME'])
        finally:
            self.avail_stream.describe(os.environ['AVAIL_STREAM_NAME'])

    def get(self):
        records = self.avail_stream.get_records(10)

        return json.dumps(records, cls=DatetimeEncoder)

    @api.expect(models[os.environ['AVAIL_SCHEMA']], validate=True)
    def post(self):

        return self.put_message(api.payload)


    def put_message(self, message):
        print(message)
        assert validators[os.environ['AVAIL_SCHEMA']].is_valid(message) is True
        date = datetime.datetime.now()
        timestamp = date.timestamp()
        response = self.avail_stream.put_record(message,'avail')

        return {"status": "posted", "schema":"avail", "timestamp":timestamp, "date":str(date), "response":json.dumps(response)}