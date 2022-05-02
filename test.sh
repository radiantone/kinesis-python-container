#!/bin/bash

cd /opt/kinesis/tests

export PYTHONPATH=.:/opt/kinesis/tests:/opt/kinesis/examples

/opt/kinesis/venv/bin/pytest .