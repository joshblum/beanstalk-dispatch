import json

import boto
from django.test import TestCase
from django.test import override_settings
from moto import mock_sqs_deprecated

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


@mock_sqs_deprecated
@override_settings(BEANSTALK_DISPATCH_SQS_KEY="", BEANSTALK_DISPATCH_SQS_SECRET="")
class ClientTestCase(TestCase):

    def setUp(self):
        self.queue_name = "testing-queue"

    def test_async_function_scheduling(self):
        # Schedule a function with a missing queue
        schedule_function(self.queue_name, "a-function", "1", "2", kwarg1=1, kwarg2=2)

        # Check the message on the queue.
        sqs_connection = boto.connect_sqs("", "")
        sqs_connection.create_queue(self.queue_name)
        queue = sqs_connection.get_queue(self.queue_name)
        messages = queue.get_messages()
        self.assertEqual(len(messages), 1)

        # For some reason, boto base64-encodes the messages, but moto
        # does not.  Life.
        self.assertEqual(
            json.loads(messages[0].get_body()),
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
