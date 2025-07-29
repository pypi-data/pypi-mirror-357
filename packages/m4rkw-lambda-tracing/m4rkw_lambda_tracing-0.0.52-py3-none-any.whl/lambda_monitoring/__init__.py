import os
import sys
import boto3
import time
import uuid
import json
import datetime
import traceback
import requests
from pushover import Client

DYNAMODB_METHODS = [
    'get_item', 'put_item', 'update_item', 'delete_item',
    'batch_get_item', 'batch_write_item',
    'query', 'scan'
]

class LambdaMonitor:

    def __init__(self, context, suffix=None):
        self.log("initialising LambdaMonitor")

        self.start_time = time.time()

        timestamp = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        self.log(f"start time: {timestamp}")

        self.function_name = context.function_name

        if suffix is not None:
            self.function_name = f"{self.function_name}_{suffix}"

        self.state = self.get_state()
        self.pushover = pushover = Client(os.environ['LAMBDA_TRACING_PUSHOVER_USER'], api_token=os.environ['LAMBDA_TRACING_PUSHOVER_APP'])

        self.track_calls = False


    def log(self, message):
        if sys.stdin.isatty():
            sys.stdout.write(message + "\n")
            sys.stdout.flush()


    def initialise_metrics(self):
        self.log(f"initialised metric counters")

        self.calls = {
        }

        for method in DYNAMODB_METHODS:
            self.calls[method] = 0

        self.metrics = {
            'read': 0,
            'write': 0,
            'delete': 0
        }


    def collect_metrics(self):
        if self.track_calls is False:
            self.initialise_metrics()
            self.patch_boto()
            self.track_calls = True


    def log_method_call(self, method_name, table):
        self.log(f"METHOD CALL: {method_name} table={table}")

        if method_name not in self.calls:
            self.calls[method_name] = 0

        self.calls[method_name] += 1


    def log_read(self, count):
        self.log(f"READ: {count}")
        self.metrics['read'] += count


    def log_write(self, count):
        self.log(f"WRITE: {count}")
        self.metrics['write'] += count


    def log_delete(self, count):
        self.log(f"DELETE: {count}")
        self.metrics['delete'] += count


    def patch_boto(self):
        original_client = boto3.client
        self.original_client = original_client
        lm = self

        def patch_method(client, method_name):
            original = getattr(client, method_name)

            def wrapper(*args, **kwargs):
                if 'TableName' not in kwargs:
                    table = list(kwargs['RequestItems'].keys())[0]
                else:
                    table = kwargs['TableName']

                lm.log_method_call(method_name, table)
                resp = original(*args, **kwargs)

                if 'Item' in resp:
                    lm.log_read(1)
                elif 'Items' in resp:
                    lm.log_read(len(resp['Items']))

                if method_name in ['put_item', 'update_item']:
                    lm.log_write(1)
                elif method_name == 'delete_item':
                    lm.log_delete(1)
                elif method_name == 'batch_write_item':
                    for key in kwargs['RequestItems']:
                        lm.log_write(len(kwargs['RequestItems'][key]))

                return resp

            setattr(client, method_name, wrapper)

        def patched_client(service_name, *args, **kwargs):
            client = original_client(service_name, *args, **kwargs)
            if service_name == 'dynamodb':
                for method in DYNAMODB_METHODS:
                    if hasattr(client, method):
                        patch_method(client, method)
            return client

        boto3.client = patched_client


    def get_state(self):
        resp = requests.get(
            os.environ['LAMBDA_TRACING_METRICS_ENDPOINT'].replace('metrics.py','state.py?function=' + self.function_name),
            timeout=10,
            auth=(os.environ['LAMBDA_TRACING_METRICS_USERNAME'], os.environ['LAMBDA_TRACING_METRICS_PASSWORD'])
        )

        data = json.loads(resp.text)

        return data


    def success(self):
        timestamp = int(time.time())
        runtime = time.time() - self.start_time

        if not self.state['success']:
            self.pushover.send_message('resolved', title=self.function_name)

        try:
            self.send_metrics(True, timestamp, runtime)
        except Exception as e:
            sys.stderr.write(f"failed to send metrics: {str(e)}\n")
            sys.stderr.flush()

            raise e


    def send_metrics(self, success, timestamp, runtime):
        self.log(f"emitting metrics:\n")
        self.log(f"success: {int(success)}\n")
        self.log(f"runtime: {runtime:.2f} seconds\n")

        for method, count in self.calls.items():
            self.log(f"{method}: {count}\n")

        for metric, count in self.metrics.items():
            self.log(f"{metric}: {count}\n")

        resp = requests.post(
            os.environ['LAMBDA_TRACING_METRICS_ENDPOINT'],
            json={
                'success': success,
                'key': self.function_name,
                'timestamp': timestamp,
                'runtime': runtime,
                'calls': self.calls,
                'metrics': self.metrics
            },
            headers={
                'Content-Type': 'application/json'
            },
            timeout=10,
            auth=(os.environ['LAMBDA_TRACING_METRICS_USERNAME'], os.environ['LAMBDA_TRACING_METRICS_PASSWORD'])
        )

        boto3.client = self.original_client


    def failure(self):
        timestamp = int(time.time())
        runtime = time.time() - self.start_time

        if self.track_calls:
            self.send_metrics(False, timestamp, runtime)

        if self.state['success']:
            exception = traceback.format_exc()

            content = f"Function: {self.function_name}\n"
            content += f"Runtime: {runtime:.2f} seconds\n"
            content += f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            content += traceback.format_exc()

            exception_endpoint = os.environ['LAMBDA_TRACING_EXCEPTION_ENDPOINT']

            url = f"{exception_endpoint}?key={self.function_name}&timestamp={int(time.time())}"

            exception = traceback.format_exception_only(*sys.exc_info()[:2])[-1].strip()

            self.pushover.send_message(exception, title=self.function_name, url=url)

        resp = requests.post(
            os.environ['LAMBDA_TRACING_METRICS_ENDPOINT'],
            json={
                'success': False,
                'key': self.function_name,
                'timestamp': timestamp,
                'runtime': runtime,
                'calls': self.calls,
                'metrics': self.metrics
            },
            headers={
                'Content-Type': 'application/json'
            },
            timeout=10,
            auth=(os.environ['LAMBDA_TRACING_METRICS_USERNAME'], os.environ['LAMBDA_TRACING_METRICS_PASSWORD'])
        )

