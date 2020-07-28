from google.cloud import iot_v1
import os
import argparse


def send_command(
        project_id, cloud_region, registry_id, device_id,
        command):
    """Send a command to a device."""
    # [START iot_send_command]
    print('Sending command to device')
    client = iot_v1.DeviceManagerClient()
    device_path = client.device_path(
        project_id, cloud_region, registry_id, device_id)

    # command = 'Hello IoT Core!'
    data = command.encode('utf-8')

    return client.send_command_to_device(device_path, data)
    # [END iot_send_command]

def parse_command_line_args():
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description=(
                'Example Google Cloud IoT Core MQTT device connection code.'))
        parser.add_argument(
                '--project_id',
                default=os.environ.get('GOOGLE_CLOUD_PROJECT'),
                help='GCP cloud project name')
        parser.add_argument(
                '--registry_id', required=True, help='Cloud IoT Core registry id')
        parser.add_argument(
                '--device_id', required=True, help='Cloud IoT Core device id')
        parser.add_argument(
                '--cloud_region', default='us-central1', help='GCP cloud region')
        parser.add_argument(
                '--mqtt_bridge_hostname',
                default='mqtt.googleapis.com',
                help='MQTT bridge hostname.')
        parser.add_argument(
                '--mqtt_bridge_port',
                default=8883,
                type=int,
                help='MQTT bridge port.')

        return parser.parse_args()

def main():
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
    
    args = parse_command_line_args()
    send_command(args.project_id, args.cloud_region, args.registry_id, args.device_id, "Test")

if __name__ == '__main__':
    main()