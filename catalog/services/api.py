from flask import Blueprint
from flask_restx import Api

from .kinesis.service import api as kinesis

api = Api(
    title="Modular API",
    version="1.0",
    description="a boilerplate for flask restplus web service",
)

# Add services to this API namespace
api.add_namespace(kinesis, path="/api/kinesis")
