import pytest
import os

os.environ['AVAIL_SCHEMA'] = './schemas/avail.json'
os.environ['AVAIL_STREAM_NAME'] = 'content-catalog-avail-test'

def test_avail_put():
    import json
    from catalog.services.kinesis.service import CatalogAvailKinesisService

    avail_service = CatalogAvailKinesisService()

    avail_message = open('schemas/messages/sample-avail.json','r')
    avail_m = avail_message.read()
    avail_msg = json.loads(avail_m)
    response = avail_service.put(avail_msg)
    assert response['status'] == 'posted'