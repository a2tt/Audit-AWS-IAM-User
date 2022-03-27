import gzip
import json
import datetime
import dateutil.parser
from base64 import b64decode

import requests

import configs


def handler(event: dict, context: dict = None):
    # Decode data
    data = event['awslogs']['data'].encode()
    data = gzip.decompress(b64decode(data)).decode()
    print(data)  # logging
    data = json.loads(data)

    trail_logs = data['logEvents']

    for trail_log in trail_logs:
        try:
            # Parse fields
            trail_data = json.loads(trail_log['message'])

            username = trail_data['userIdentity']['userName']
            if username in configs.IGNORE_USER:
                continue

            ip = trail_data['sourceIPAddress']
            event_time = ((dateutil.parser.parse(trail_data['eventTime'])
                           + datetime.timedelta(hours=9)).strftime('%Y.%m.%d %H:%M:%S'))
            event_type = trail_data['eventType']
            event_source = trail_data['eventSource']
            event_name = trail_data['eventName']
            region = trail_data['awsRegion']

            event_id = trail_data['eventID']
            trail_url = configs.CLOUDTRAIL_URL.format(event_id)

            # Prepare payload
            payload = {
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': '\n'.join([
                                f"*{username} ({ip})*",
                                f'Time: {event_time}',
                                f'Type: {event_type}',
                                f'Source: {event_source}',
                                f'Name: {event_name}',
                                f'Region: {region}',
                                f''
                            ]),
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f'_<{trail_url}|{event_id}>_',
                        }
                    }
                ]
            }
        except json.JSONDecodeError:
            payload = {
                'blocks': [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f'```{trail_log}```',
                        }
                    }
                ]
            }

        # Send to slack
        resp = requests.post(configs.WEBHOOK_URL, json=payload)
        print(resp.text, resp.status_code)


if __name__ == '__main__':
    # awslogs.data: gzip-compressed and base64 encoded
    handler({
        # The following is the 'cloudwatch-logs' test sample of Lambda,
        # but note that, it does not meet the format we are receiving in the real case.
        "awslogs": {
            "data": "H4sIAAAAAAAAAHWPwQqCQBCGX0Xm7EFtK+smZBEUgXoLCdMhFtKV3akI8d0bLYmibvPPN3wz00CJxmQnTO41whwWQRIctmEcB6sQbFC3CjW3XW8kxpOpP+OC22d1Wml1qZkQGtoMsScxaczKN3plG8zlaHIta5KqWsozoTYw3/djzwhpLwivWFGHGpAFe7DL68JlBUk+l7KSN7tCOEJ4M3/qOI49vMHj+zCKdlFqLaU2ZHV2a4Ct/an0/ivdX8oYc1UVX860fQDQiMdxRQEAAA=="
        }
    })

    # Decoded data
    # {
    #     "messageType": "DATA_MESSAGE",
    #     "owner": "<Owner ID>",
    #     "logGroup": "<Log Group Name>",
    #     "logStream": "<Log Stream Name>>",
    #     "subscriptionFilters": ["IAMUser"],
    #     "logEvents": [
    #         {
    #             "id": "36760379218472725949553766780520120265769208210171953000",
    #             "timestamp": 1648392414299,
    #             "message": "<JSON object>"
    #         }
    #     ]
    # }
