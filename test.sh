#!/bin/bash
export PROJECT_ID=letterbot-staging
export MY_REGION=asia-east1


python receive.py --project_id=$PROJECT_ID --cloud_region=$MY_REGION --registry_id=test --device_id=adwin-macbook2 --private_key_file=rsa_private.pem --algorithm=RS256

sleep 2

python push_data_to_device.py --project_id=$PROJECT_ID --cloud_region=$MY_REGION --registry_id=test --device_id=adwin-macbook2