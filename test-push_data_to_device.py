import argparse
import base64
import json
import os
import sys
from threading import Lock
import time

from google.cloud import pubsub
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.errors import HttpError

API_SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
API_VERSION = 'v1'
DISCOVERY_API = 'https://cloudiot.googleapis.com/$discovery/rest'
SERVICE_NAME = 'cloudiot'

class Server(object):
        """Represents the state of the server."""
        def __init__(self, service_account_json):
                credentials = service_account.Credentials.from_service_account_file(
                service_account_json).with_scopes(API_SCOPES)
                if not credentials:
                        sys.exit('Could not load service account credential '
                        'from {}'.format(service_account_json))

                discovery_url = '{}?version={}'.format(DISCOVERY_API, API_VERSION)

                self._service = discovery.build(
                        SERVICE_NAME,
                        API_VERSION,
                        discoveryServiceUrl=discovery_url,
                        credentials=credentials,
                        cache_discovery=False)

                # Used to serialize the calls to the
                # modifyCloudToDeviceConfig REST method. This is needed
                # because the google-api-python-client library is built on top
                # of the httplib2 library, which is not thread-safe. For more
                # details, see: https://developers.google.com/api-client-library/python/guide/thread_safety
                self._update_config_mutex = Lock()
        
        def _update_device_config(self, project_id, region, registry_id, device_id,
                              data):
            """Push the data to the given device as configuration."""
            body = {
                # The device configuration specifies a version to update, which
                # can be used to avoid having configuration updates race. In this
                # case, you use the special value of 0, which tells Cloud IoT to
                # always update the config.
                'version_to_update': 0,
                # The data is passed as raw bytes, so you encode it as base64.
                # Note that the device will receive the decoded string, so you
                # do not need to base64 decode the string on the device.
                'binary_data': base64.b64encode(
                        data.encode('utf-8')).decode('ascii')
            }

            device_name = ('projects/{}/locations/{}/registries/{}/'
                        'devices/{}'.format(
                            project_id,
                            region,
                            registry_id,
                            device_id))

            request = self._service.projects().locations().registries().devices(
            ).modifyCloudToDeviceConfig(name=device_name, body=body)

            # The http call for the device config change is thread-locked so
            # that there aren't competing threads simultaneously using the
            # httplib2 library, which is not thread-safe.
            self._update_config_mutex.acquire()
            try:
                request.execute()
            except HttpError as e:
                # If the server responds with a HtppError, log it here, but
                # continue so that the message does not stay NACK'ed on the
                # pubsub channel.
                print('Error executing ModifyCloudToDeviceConfig: {}'.format(e))
            finally:
                self._update_config_mutex.release()

def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Example of Google Cloud IoT registry and '
                    'device management.')

    # Required arguments
    parser.add_argument(
        '--project_id',
        default=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        required=True,
        help='GCP cloud project name.')

    parser.add_argument(
        '--registry_id', 
        required=True, 
        help='Cloud IoT Core registry id')
    
    parser.add_argument(
        '--device_id', 
        required=True, 
        help='Cloud IoT Core device id')

    # Optional arguments
    parser.add_argument(
        '--service_account_json',
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        help='Path to service account json file.')
    
    parser.add_argument(
        '--cloud_region', 
        default='asia-east1', 
        help='GCP cloud region')
    


    return parser.parse_args()

def main():
    args = parse_command_line_args()

    server = Server(args.service_account_json)
    for i in range(5):
        server._update_device_config(args.project_id, args.cloud_region, args.registry_id, args.device_id, "This is data {}".format(i))
        time.sleep(1)
if __name__ == '__main__':
    main()