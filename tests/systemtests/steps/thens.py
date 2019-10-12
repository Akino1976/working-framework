import time
import os
import json
import datetime

from pytest_bdd import then, parsers

import helpers.aws as aws


@then(parsers.parse('the return code should be {return_code}'))
def check_return_code(return_code, request):
    if 'ERROR' in request.process.stdoutdata:
        returncode = 1
    else:
        returncode = 0

    assert returncode == int(return_code)


@then(parsers.parse('there should be a file in S3 like:\n{yaml_string}'))
def get_file_from_bucket(yaml_string: str, request: object):
    options = yaml.load_with_tags(request, yaml_string)
    dynamic_date = options.get('dynamic_date', False)
    client = aws.get_client('s3')

    response = client.list_objects_v2(Bucket=options['bucket'])

    keys = [
        obj['Key'] for obj in response.get('Contents', '')
    ]
    if len(keys) > 0:
        keys =  keys[0]

    assert options['key'] in keys

    response = client.get_object(
        Bucket=options['bucket'],
        Key=keys
    )
    decoded_content = response['Body'].read().decode('utf-8')

    if len(decoded_content) > 2:
        decoded_content = [
            json.loads(row)
            for row in decoded_content.split('\n')
            if len(row) > 0
        ]

    if dynamic_date:
        for value in decoded_content:
            value[dynamic_date] = datetime.datetime.now().strftime('%Y-%m-%d')

    assert options.get('content') is None or comparisons.contains(decoded_content, options['content'])
    assert comparisons.contains(
        response['Metadata'],
        options.get('meta_data', {}),
    )


@then(parsers.parse('there are no new objects in the {bucket} bucket'))
def no_new_s3_objects(bucket, bucket_objects, request):
    bucket_name = yaml.load_with_tags(request, bucket)

    assert comparisons.contains(
        aws.list_object_names(bucket_name),
        bucket_objects
    )


@then('I want to use pdb')
def use_pdb(request):
    pdb.set_trace()
