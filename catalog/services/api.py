from flask import Blueprint
from flask_restx import Api

from .kinesis.service import api as kinesis

api = Api(
    title="Kinesis Producer API",
    version="1.0",
    description="Content Catalog Kinesis Producer Micro-Service",
)

# Add services to this API namespace
api.add_namespace(kinesis, path="/api/kinesis")
