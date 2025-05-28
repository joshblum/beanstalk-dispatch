import json
from base64 import b64decode

import boto3
from django.test import TestCase
from django.test import override_settings
from moto import mock_aws

from ..client import schedule_function
from ..common import ARGS
from ..common import FUNCTION
from ..common import KWARGS

CALL_COUNTER = 0


def counter_incrementer(first_arg, second_arg=None):
    global CALL_COUNTER
    CALL_COUNTER += first_arg
    if second_arg:
        CALL_COUNTER += second_arg


DISPATCH_SETTINGS = {
    "BEANSTALK_DISPATCH_TABLE": {
        "the_counter": ("beanstalk_dispatch.tests." "test_client.counter_incrementer")
    }
}


@mock_aws
@override_settings(BEANSTALK_DISPATCH_SQS_KEY="", BEANSTALK_DISPATCH_SQS_SECRET="")
class ClientTestCase(TestCase):

    def setUp(self):
        self.queue_name = "testing-queue"

    def test_async_function_scheduling(self):
        # Schedule a function with a missing queue
        schedule_function(self.queue_name, "a-function", "1", "2", kwarg1=1, kwarg2=2)

        # Check the message on the queue.
        sqs = boto3.client("sqs", region_name="us-east-1")
        queue_url = sqs.create_queue(QueueName=self.queue_name)["QueueUrl"]

        # Get messages from the queue
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

        messages = response.get("Messages", [])
        self.assertEqual(len(messages), 1)

        message_body = messages[0]["Body"]
        body_content = json.loads(b64decode(message_body).decode())

        self.assertEqual(
            body_content,
            {
                FUNCTION: "a-function",
                ARGS: ["1", "2"],
                KWARGS: {"kwarg1": 1, "kwarg2": 2},
            },
        )

    @override_settings(
        BEANSTALK_DISPATCH_EXECUTE_SYNCHRONOUSLY=True, **DISPATCH_SETTINGS
    )
    def test_sync_function_scheduling(self):
        # Schedule a function.
        schedule_function(self.queue_name, "the_counter", 1, second_arg=5)

        self.assertEqual(CALL_COUNTER, 6)
