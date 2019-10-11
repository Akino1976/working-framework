import sys
import os

import yaml
import logging.config

from optparse import OptionParser
from dotenv import load_dotenv


BASE_PATH = os.sep.join(
    os.path.realpath(__file__).split(os.sep)[:-1]
)

log_file_path = os.path.join(BASE_PATH, 'output/logs')
os.makedirs(log_file_path, exist_ok=True)

with open(os.path.join(BASE_PATH, 'logging.yaml'), 'r') as stream:
    config = yaml.safe_load(stream.read())

    for file_handler in ['error_file_handler', 'info_file_handler']:

        change_path = config['handlers'][file_handler]['filename']
        config['handlers'][file_handler]['filename'] = os.path.join(
            BASE_PATH, change_path
        )
    logging.config.dictConfig(config)

parser = OptionParser()
parser.add_option(
    '-f',
    '--file',
    action='store',
    type='string',
    dest='file'
)
parser.add_option(
    '-e',
    '--environment',
    default='dev',
    action='store',
    type='string',
    dest='environment'
)
parser.add_option(
    '-q',
    '--queue',
    default='formatted',
    action='store',
    type='string',
    dest='queue'
)

options, args = parser.parse_args()

ENVIRONMENT = 'test'


ignored_file_path = os.path.join(
    os.path.dirname(BASE_PATH),
    '.ignored'
)
dotenv_path = os.path.join(
    ignored_file_path,
    f'.env_{ENVIRONMENT}'
)
load_dotenv(dotenv_path)

ENCODING = 'utf-8'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_REGION = os.getenv('AWS_REGION')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')
API_BASE_HOST = os.environ.get('API_BASE_HOST')
QUEUE_NAME = os.environ.get('QUEUE_NAME')
MOTO_HOST = os.environ.get('MOTO_HOST')
QUEUE_URL = os.environ.get('QUEUE_URL')
BUCKET = os.environ.get('BUCKET')
DSN = os.environ.get('DSN')
