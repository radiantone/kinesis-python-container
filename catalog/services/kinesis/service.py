
import json
import os
import time
import logging
import datetime

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.DEBUG
)

from flask_restx import Namespace, Resource, fields
from jsonschema import (
    Draft7Validator,
    FormatChecker,
)
from botocore.exceptions import ClientError

api = Namespace("kinesis", "Kinesis service for Content Catalog", validate=True)

message_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    'type': 'object',
    'properties': {
        'param1': {'type': 'string'},
        'age': {'type': 'number'},
        'date': {"type": "string"},
    },
    'required': ['param1','date'],
}
message_model = api.schema_model('message', message_schema)
validator = Draft7Validator(message_schema, format_checker=FormatChecker())

from .fixtures.common import fixture_make_stubber

print("PARTITION KEY",os.environ['PARTITION_KEY'])

@api.route("/")
class CatalogKinesisService(Resource):

    def get(self):
        return {"status": "ok"}

    def post_kinesis(self, message):
        try:
            response = self.kinesis_client.put_record(
                StreamName=self.name,
                Data=json.dumps(message),
                PartitionKey=os.environ['PARTITION_KEY'])

            logging.info(response)
        except ClientError as ex:
            logging.error(ex)
            raise
        else:
            return response
            
    @api.expect(message_model, validate=True)
    def post(self):
        assert validator.is_valid(api.payload) is True
        date = datetime.datetime.now()
        timestamp = date.timestamp()
        #self.post_kinesis(api.payload)
        return {"status": "posted", "timestamp":timestamp, "date":str(date)}
