# beanstalk-dispatch

[![PyPI version](https://badge.fury.io/py/beanstalk-dispatch.svg?maxAge=2592000)](https://badge.fury.io/py/beanstalk-dispatch)
[![PyPI](https://img.shields.io/pypi/pyversions/beanstalk-dispatch.svg)](https://pypi.python.org/pypi/beanstalk-dispatch)
[![Github Actions](https://github.com/joshblum/beanstalk-dispatch/actions/workflows/ci.yml/badge.svg)](https://github.com/joshblum/beanstalk-dispatch/actions)

`beanstalk-dispatch` is a Django application that runs functions that have been
scheduled to run an [AWS SQS](https://aws.amazon.com/sqs/) queue and executes
them on [Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/) Worker
machines that are listening to that queue.

This application was originally written by [@marcua](https://github.com/marcua)
for [@b12io](https://github.com/b12io)'s open source application
[orchestra](https://github.com/b12io/orchestra).

The library supports Django 3 to Django 5.2 across Python versions 3.8 to
3.12. If you would like to see a feature or find a bug, please let me know by
opening an [issue](https://github.com/joshblum/beanstalk-dispatch/issues) or
[pull request](https://github.com/joshblum/beanstalk-dispatch/pulls).

## Getting started in 5 minutes

To install:

```
pip install beanstalk-dispatch
```

- create an Elastic Beanstalk environment for an application
  that has the following two parameters in `settings.py`:

```python
     BEANSTALK_DISPATCH_SQS_KEY = 'your AWS key for accessing SQS'
     BEANSTALK_DISPATCH_SQS_SECRET = 'your AWS secret for accessing SQS'
```

- Add `beanstalk_dispatch` to settings.py's `INSTALLED_APPS`

```python
INSTALLED_APPS = (
    # ...other installed applications...
    'beanstalk_dispatch',
)
```

- Add `url(r'^beanstalk_dispatch/', include('beanstalk_dispatch.urls')),` to
  your main `urls.py`

- Add `/beanstalk_dispatch/dispatcher` as the HTTP endpoint or your beanstalk
  worker configuration in the AWS console.

- Add a dispatch table. The dispatcher works by creating an HTTP endpoint
  that a local SQS/Beanstalk daemon POSTs requests to. That endpoint
  consults a `BEANSTALK_DISPATCH_TABLE`, which maps function names onto
  functions to run. Here's an example:

```python
      if os.environ.get('BEANSTALK_WORKER') == 'True':
        BEANSTALK_DISPATCH_TABLE = {
            'a_function_to_dispatch': ('some_package.beanstalk_tasks.'
                                      'the_name_of_the_function_in_the_module')
        }
```

The first line is a check we have that ensures this type of machine should
be a beanstalk worker. We set a `BEANSTALK_WORKER` environment variable to
`'True'` in the environment's configuration only on our worker machines.
This avoids other environments (e.g., our web servers) from serving as open
proxies for running arbitrary code.

The second line is the dispatch table. It maps a path to the function to be
executed.

## Scheduling a function to run

The `beanstalk_dispatch.client.schedule_function` schedules a function to run
on a given SQS queue. The function name you pass it must be a key in the
`BEANSTALK_DISPATCH_TABLE`, and the `queue_name` you pass it must be a queue
for which a beanstalk worker is configured.

```python
from beanstalk_dispatch.client import schedule_function

schedule_function('a-queue', 'a_function_to_dispatch',
    '1', '2', kwarg1=1, kwarg2=2)
```

## SafeTasks

By default, every function run by `beanstalk_dispatch` is wrapped in a
`SafeTask` class that sets a `@timeout` decorator on the function and catches
any exceptions for logging. If you would like to customize the behavior of the
`SafeTask`, create a subclass and reference this object in
`BEANSTALK_DISPATCH_TABLE`.

The following parameters/functions are configurable on a `SafeTask`

`timeout_timedelta`: maximum number of seconds task can run, defaults to `2`
minutes.
`verbose`: boolean specifying if failures are logged, defaults to `False`.
`run`: abstract method to fill in with task work.
`on_error`: a function that runs if the task fails for any reason.
`on_success`: a function that runs after the task completes successfully.
`on_completion`: a function that runs after each task (after `on_error` or
`on_success`).

For example:

```python
# beanstalk_tasks.py
from datetime import timedelta

from beanstalk_dispatch.client import schedule_function
from beanstalk_dispatch.safe_task import SafeTask

class MySafeTask(SafeTask):

    timeout_timedelta = timedelta(seconds=1000)
    verbose = True

    def run(self, *args, **kwargs):
        # Run the task
        print('Running task')

    def on_error(self, e, *args, **kwargs):
        print('There was an error {}'.format(e))

    def on_success(self, *args, **kwargs):
        print('Success!')

    def on_completion(self, *args, **kwargs):
        print('Task completed')

schedule_function('a-queue', 'mysafetask',
    '1', '2', kwarg1=1, kwarg2=2)
```

```
# settings.py
  if os.environ.get('BEANSTALK_WORKER') == 'True':
    BEANSTALK_DISPATCH_TABLE = {
        'mysafetask': 'beanstalk_tasks.MySafeTask'
    }
```
