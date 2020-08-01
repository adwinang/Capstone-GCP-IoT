import argparse
import datetime
import json
import os
import ssl
import time

import paho.mqtt.client as mqtt
from connection import create_jwt, error_str

class Device(object):
    """Represents the state of a single device."""

    def __init__(self):
        self.value = 0
        self.activate = False
        self.connected = False

    def update(self):
        """This function will update the variables
        """
        if self.activate:
            self.value -= 1
        else:
            self.value += 1
        
        print("Current Value: {}".format(self.value))

    def wait_for_connection(self, timeout):
        """Wait for the device to become connected."""
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        print('Disconnected:', error_str(rc))
        self.connected = False

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Callback when the device receives a PUBACK from the MQTT bridge."""
        print('Published message acked.')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                     granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_message(self, unused_client, unused_userdata, message):
        """Callback when the device receives a message on a subscription."""
        payload = message.payload.decode('utf-8')
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

        # The device will receive its latest config when it subscribes to the
        # config topic. If there is no configuration for the device, the device
        # will receive a config with an empty payload.
        if not payload:
            return

        print(payload)

        if self.activate:
            self.activate = False
        else:
            self.activate = True


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
                '--private_key_file',
                required=True, help='Path to private key file.')
        parser.add_argument(
                '--algorithm',
                choices=('RS256', 'ES256'),
                required=True,
                help='Which encryption algorithm to use to generate the JWT.')
        parser.add_argument(
                '--cloud_region', default='asia-east1', help='GCP cloud region')
        parser.add_argument(
                '--ca_certs',
                default='roots.pem',
                help=('CA root from https://pki.google.com/roots.pem'))
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
    args = parse_command_line_args()

    # Create our MQTT client. The client_id is a unique string that identifies
    # this device. For Google Cloud IoT Core, it must be in the format below.
    client = mqtt.Client(
            client_id=('projects/{}/locations/{}/registries/{}/devices/{}'
                    .format(
                            args.project_id,
                            args.cloud_region,
                            args.registry_id,
                            args.device_id)))

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    args.project_id, args.private_key_file, args.algorithm))

    
    # Enable SSL/TLS support.
    client.tls_set(ca_certs=args.ca_certs)

    device = Device()

    client.on_connect = device.on_connect
    client.on_publish = device.on_publish
    client.on_disconnect = device.on_disconnect
    client.on_subscribe = device.on_subscribe
    client.on_message = device.on_message

    client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

    client.loop_start()

    mqtt_command_topic = '/device/{}/commands/#'.format(args.device_id)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(args.device_id)

    device.wait_for_connection(5)

    client.subscribe(mqtt_config_topic, qos=1)

    while (device.value > -100 or device.value < 100):
        device.update()
        time.sleep(1)

    client.disconnect()
    client.loop_stop()
    print('Finished loop successfully. Goodbye!')

if __name__ == '__main__':
    main()

#python receive.py --project_id=letterbot-staging --registry_id=test --device_id=adwin-macbook --private_key_file=rsa_private.pem --algorithm=RS256