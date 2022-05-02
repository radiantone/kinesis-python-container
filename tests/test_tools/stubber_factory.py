# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
A factory function that returns the stubber for an AWS service, based on the
name of the service that is used by Boto 3.

This factory is used by the make_stubber fixture found in the set of common fixtures.
"""

from test_tools.apigateway_stubber import ApiGatewayStubber
from test_tools.kinesis_stubber import KinesisStubber

class StubberFactoryNotImplemented(Exception):
    pass


def stubber_factory(service_name):
    if service_name == 'apigateway':
        return ApiGatewayStubber
    elif service_name == 'kinesis':
        return KinesisStubber
    else:
        raise StubberFactoryNotImplemented(
            "If you see this exception, it probably means that you forgot to add "
            "a new stubber to stubber_factory.py.")
