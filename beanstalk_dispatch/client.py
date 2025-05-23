import json

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from .common import create_request_body
from .execution import execute_function


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
            aws_access_key_id=settings.BEANSTALK_DISPATCH_SQS_KEY,
            aws_secret_access_key=settings.BEANSTALK_DISPATCH_SQS_SECRET,
        )

        try:
            queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
        except ClientError as e:
            if "NonExistentQueue" in str(e) or "QueueDoesNotExist" in str(e):
                queue_url = sqs.create_queue(QueueName=queue_name)["QueueUrl"]
            else:
                raise ClientError(e)

        sqs.send_message(QueueUrl=queue_url, MessageBody=body)
