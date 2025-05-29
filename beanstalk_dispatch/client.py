import base64
import json

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from .common import create_request_body
from .execution import execute_function


def encode_message(value):
    """
    Encode the message in the same way boto2 did with queue.write(message)
    """
    if not isinstance(value, bytes):
        value = value.encode("utf-8")
    return base64.b64encode(value).decode("utf-8")


def schedule_function(queue_name, function_name, *args, **kwargs):
    """
    Schedule a function named `function_name` to be run by workers on
    the queue `queue_name` with *args and **kwargs as specified by that
    function.
    """
    body = create_request_body(function_name, *args, **kwargs)
    if getattr(settings, "BEANSTALK_DISPATCH_EXECUTE_SYNCHRONOUSLY", False):
        execute_function(json.loads(body))
    else:
        sqs = boto3.client(
            "sqs",
            region_name=getattr(settings, "BEANSTALK_DISPATCH_SQS_REGION", "us-east-1"),
            aws_access_key_id=settings.BEANSTALK_DISPATCH_SQS_KEY,
            aws_secret_access_key=settings.BEANSTALK_DISPATCH_SQS_SECRET,
        )

        try:
            queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
        except ClientError as e:
            if "NonExistentQueue" in str(e) or "QueueDoesNotExist" in str(e):
                queue_url = sqs.create_queue(QueueName=queue_name)["QueueUrl"]
            else:
                raise

        encoded_body = encode_message(body)
        sqs.send_message(QueueUrl=queue_url, MessageBody=encoded_body)
