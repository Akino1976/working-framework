import os

INPUT_BUCKET = os.getenv('INPUT_BUCKET')
OUTPUT_BUCKET = os.getenv('OUTPUT_BUCKET')
AGGREGATED_BUCKET = os.getenv('AGGREGATED_BUCKET')
AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath('../tmp/')
