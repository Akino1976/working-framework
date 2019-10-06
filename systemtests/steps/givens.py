
import os
import shutil
import json
import datetime

from pytest_bdd import given, parsers

from botocore.client import ClientError

import helpers.aws as aws
import settings


@given(parsers.parse('the entrypoint "{entrypoint_str}"'), target_fixture='entrypoint')
def set_entrypoint(entrypoint_str):
    return entrypoint_str.split()


@given(parsers.parse('the command "{command_str}"'), target_fixture='command')
def set_command(command_str):
    return command_str.split()


@given(parsers.parse('the flags "{flags}"'), target_fixture='flags')
def set_flag(flags):
    return flags


@given(parsers.parse('there is a file in S3 like:\n{yaml_string}'))
def put_file_in_bucket(yaml_string: str, request: object):
    options = yaml.load_with_tags(request, yaml_string)

    client = aws.get_client('s3')

    client.put_object(
        Bucket=options['bucket'],
        Key=options['key'],
        Body=options['content'],
    )


@given(parsers.parse('the bucket {bucket_name} is empty'))
def empty_bucket(bucket_name):
    aws.empty_bucket(bucket_name)


@given(parsers.parse('the bucket {bucket_name} is empty'))
def named_bucket(request, bucket_name):
    options = yaml.load_with_tags(request, bucket_name)
    aws.empty_bucket(bucket=options)

