from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from google.oauth2 import service_account
import os


# TODO(developer)
project_id = "letterbot-staging"
subscription_id = "anotherTest"
# Number of seconds the subscriber should listen for messages
# timeout = 5.0
service_account_json="/Volumes/Samsung_T5/School/Capstone/Python/gcp/Capstone-GCP-IoT/service_account.json"
API_SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
API_VERSION = 'v1'
DISCOVERY_API = 'https://cloudiot.googleapis.com/$discovery/rest'
SERVICE_NAME = 'cloudiot'

credentials = service_account.Credentials.from_service_account_file(
    service_account_json).with_scopes(API_SCOPES)
if not credentials:
    sys.exit('Could not load service account credential '
                'from {}'.format(service_account_json))

subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    print("Received message: {}".format(message))
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print("Listening for messages on {}..\n".format(subscription_path))

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()