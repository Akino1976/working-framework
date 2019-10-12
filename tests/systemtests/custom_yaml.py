import os
import json
import uuid

from utils import yaml


class CompareSingleValueMeta(metaclass=yaml.MatchAll):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        class_name = self.__class__.__name__

        props = ', '.join([
            f'{propname}={value}'
            for propname, value in self.__dict__.items()
        ])

        return f'{class_name}({props})'


class IgnoreSurroundingWhitespace(CompareSingleValueMeta):
    def __eq__(self, other):
        if isinstance(other, KeyError):
            raise other

        if isinstance(other, str):
            return other.strip() == self.value.strip()

        return False


@yaml.yaml_tag('!IgnoreSurroundingWhitespace')
def ignore_surrounding_whitespace(loader, tag_suffix, node):
    return IgnoreSurroundingWhitespace(loader.construct_scalar(node))


@yaml.yaml_tag('!WithEncoding')
def with_encoding(loader, tag_suffix, node):
    flattened = dict(loader.construct_pairs(node))

    return flattened['content'].encode(flattened['encoding'])


@yaml.yaml_tag('!AsSQSMessage')
def as_sqs_message(loader, tag_suffix, node):
    return {
        'Records': [
            {
                'messageId': 'ac9064ab-3a27-4221-bfda-2f8f0a5e7ae5',
                'receiptHandle': 'AQEBye/N/wTvnLnT5JDArO63MqFmdyKwRCKOkmiWw+Mrhcn1FLJJSe13pgRiQe4giQqp3TpJCspWIHcTd5Y6epI5CjVgaHx/dEVeucvOppLWucRNfAWPF5UBk/EXUMtvTe3uevksqud00DuhZaoJfrO+kLcM/wZ7oot4J0319fFadqQA+A8buh6nEXtsfqoF7pHPu8ihkUvGSGIh5Pt0vFUIopoQJjSw/OiPEik5K2HJnehr90uo3I0v/K9o7ax/IdiryPAd0/8vb6m10tspTNWu5vyPws95cvymTmRvaXB9IUhkLde7s5FuGw08jrgZyfsdKtrqkQ7kRRsY4LZU2/Vp2SummX3ldUU7TXTTSe8GVQW/r8tPWBb+s6Xsp3SIdvbXETLUpgUKe7EMhli8Pe/yFe9cP5GnndfctgncUyHpPSGPA9UXeYSwJB3BCXpJ1omf',
                'body': json.dumps({
                    'Type': 'Notification',
                    'MessageId': 'a990f1e5-cfab-5f93-9e79-a4af8d159fb1',
                    'TopicArn': 'arn:aws:sns:eu-west-1:254506858912:storage-queue-docker-eu-west-1',
                    'Subject': 'Amazon S3 Notification',
                    'Message': json.dumps({
                        'Records': [
                            {
                                'eventVersion': '2.1',
                                'eventSource': 'aws:s3',
                                'awsRegion': 'eu-west-1',
                                'eventTime': '2019-05-06T14:34:19.732Z',
                                'eventName': 'ObjectCreated:CompleteMultipartUpload',
                                'userIdentity': {
                                    'principalId': 'AWS:AISDOAISDA:blabla@email.com'
                                },
                                'requestParameters': {
                                    'sourceIPAddress': '123.12.12.123'
                                },
                                'responseElements': {
                                    'x-amz-request-id': '8732859923746593C',
                                    'x-amz-id-2': 'oaisjdaisdJOAISJDOIAjdijsadiaJPOAISD='
                                },
                                's3': {
                                    's3SchemaVersion': '1.0',
                                    'configurationId': 'abc123-1234-1323-1231-12312123134',
                                    'bucket': {
                                        'name': 'storage-docker-eu-west-1',
                                        'ownerIdentity': {'principalId': 'AZXMVRRHVZYLV'},
                                        'arn': 'arn:aws:s3:::storage-docker-eu-west-1'
                                    },
                                    'object': loader.construct_mapping(node, deep=True),
                                }
                            }
                        ]
                    }),
                    'Timestamp': '2019-05-06T14:11:10.222Z',
                    'SignatureVersion': '1',
                    'Signature': 'mHfgtiQq5hA5JwkUn4BQYzPF8wUI1OuZ5aJf7sLjHLs+M/0ZhtXdMYR4kpFzWzhzRcA/xBo9ipF+xCmElcenaXmz1RJEvI9e/Ax0XIUHZCPXDwoCGYw95/FLrsZtY3n38XPrG3qC02RIxLsZNJgt4Sx+EbsptqLuDDLNSbLolQV1gHpYQSy/b/h0BNCRnuZ4i2Sswu+eP7NtLwukMMfwufpqo1eN6zQUpkU+I6OlX34FQ/zCxAW7E2wt8710gcnDSEFsw1xBAsCpFOiVj6fp1ISK7jhXeV9syoBVDEAStUVqM6udFC4TBp/l7obEdtt8eplkp74ogfUpd93EglLG2g==',
                    'SigningCertURL': 'https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-6aad65c2f9911b05cd53efda11f913f9.pem',
                    'UnsubscribeURL': 'https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-west-1:254506858912:storage-queue-docker-eu-west-1:6a86664f-7019-4b74-a059-8f4db559688e'
                }),
                'attributes': {
                    'ApproximateReceiveCount': '1',
                    'SentTimestamp': '1557151870292',
                    'SenderId': 'AIDAISMY7JYY5F7RTT6AO',
                    'ApproximateFirstReceiveTimestamp': '1557151870297'
                },
                'messageAttributes': {},
                'md5OfBody': '16228f4fb709388ff481c1deaf86c35d',
                'eventSource': 'aws:sqs',
                'eventSourceARN': 'arn:aws:sqs:eu-west-1:254506858912:storage-queue-docker-eu-west-1',
                'awsRegion': 'eu-west-1'
            }
        ]
    }

class ContainsString(CompareSingleValueMeta):
    def __eq__(self, other):
        if isinstance(other, str):
            return -1 < other.find(self.value)

        return False


@yaml.yaml_tag('!ContainsString')
def contains_string(loader, tag_suffix, node):
    return ContainsString(loader.construct_scalar(node))


@yaml.yaml_tag('!FromFile')
def from_file(loader, tag_suffix, node):
    filepath = os.path.join(
        settings.PROJECT_ROOT,
        loader.construct_scalar(node),
    )

    with open(filepath) as file:
        return file.read()


class IsOfLength(CompareSingleValueMeta):
    def __eq__(self, other):
        if not hasattr(other, '__len__'):
            raise NotImplemented

        return self.value == len(other)


@yaml.yaml_tag('!IsOfLength')
def is_of_length(loader, tag_suffix, node):
    return IsOfLength(int(loader.construct_scalar(node)))


class HasRowCount(CompareSingleValueMeta):
    def __eq__(self, other):
        if not hasattr(other, 'split'):
            raise NotImplemented

        return self.value == len(other.split('\n'))


@yaml.yaml_tag('!HasRowCount')
def is_of_length(loader, tag_suffix, node):
    return HasRowCount(int(loader.construct_scalar(node)))


@yaml.yaml_tag('!BytesFromFile')
def read_file_bytes(loader, tag_suffix, node) -> bytes:
    filepath = loader.construct_scalar(node)

    with open(filepath, 'rb') as file:
        return file.read()
