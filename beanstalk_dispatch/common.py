import json

ARGS = 'args'
FUNCTION = 'function'
KWARGS = 'kwargs'


class BeanstalkDispatchError(Exception):
    pass


def create_request_body(function_name, *args, **kwargs):
    return json.dumps({FUNCTION: function_name, ARGS: args, KWARGS: kwargs})
