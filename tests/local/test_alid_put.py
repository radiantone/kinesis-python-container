import pytest
import os

os.environ['ALID_SCHEMA'] = './schemas/alid.json'
os.environ['ALID_STREAM_NAME'] = 'content-catalog-alid-test'

def test_alid_put():
    import json
    from catalog.services.kinesis.service import CatalogAlidKinesisService

    alid_service = CatalogAlidKinesisService()

    alid_message = open('schemas/messages/sample-alid.json','r')
    alid_m = alid_message.read()
    alid_msg = json.loads(alid_m)
    response = alid_service.put(alid_msg)
    assert response['status'] == 'posted'