import gate_api
from gate_api.exceptions import ApiException, GateApiException
import pytz
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import hmac
import hashlib
import time
import json
import csv
from datetime import datetime
import pytz

from .csv_generator import generate_csv_file

ASCENDEX_API_URL = "https://ascendex.com/api/pro/v1/wallet/transactions"


class AscendexApi():
    def __init__(self, input_dict):
        self.api_key = input_dict.get('api_key')
        self.secret = input_dict.get('secret')
        self.api_action = input_dict.get('apiaction')

        self.initiate_request()

    def initiate_request(self):
        if self.api_action == 'deposits_and_withdraws':
            self.get_deposits_and_withdraws()

    def get_deposits_and_withdraws(self):
        # deposit / withdraws
        url = 'https://ascendex.com/api/pro/v1/wallet/transactions'

        # api_key = 'y9jqRqsLGyRccAi4A9Oee8xLIrEBWlZf'
        # secret = 'ieazhhHVjBthxmU5HJhD6pyzBP8cVDbKnmQHmLIYRuApWISssuzIVGzCBNwW3mxT'

        timestamp  = int(time.time() * 1000)
        api_path = 'wallet/transactions'
        pre_hash_msg = f'{timestamp}+{api_path}'.encode('utf-8')

        hmac_sha256 = hmac.new(
            self.secret.encode('utf-8'),
            pre_hash_msg,
            hashlib.sha256).digest()

        signature = base64.b64encode(hmac_sha256).decode('utf-8')

        headers = {
            'x-auth-key': self.api_key,
            'x-auth-timestamp': str(timestamp),
            'x-auth-signature': signature
        }
        deposits_and_withdraws = []
        current_page = 1
        last_page_reached = False
        while last_page_reached == False:
            params = dict(
            page=current_page,
            pageSize=50)

            response = requests.get(url, params, headers=headers)
            response_content = json.loads(response.content)
            response_data = response_content.get('data').get('data')

            if len(response_data) > 0:
                deposits_and_withdraws.extend(response_data)
                current_page+=1
            else:
                last_page_reached = True

        csv_header = ['Koinly Date', 'Amount', 'Currency', 'Label', 'TxHash']
        try:
            with open('ascendex_deposits_and_withdraws.csv', 'w', encoding='UTF8') as f:
                    writer = csv.DictWriter(f, fieldnames=csv_header)
                    writer.writeheader()
                    trades = ({
                        #TODO: confirm if create_time is in seconds
                        'Koinly Date': datetime.fromtimestamp(int(trade['time']/1000), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                        'Amount': trade['amount'],
                        'Currency': trade['asset'],
                        #TODO: confirm the field
                        'Label': trade['status'],
                        #TODO: confirm the field
                        'TxHash': trade['requestId'],
                        } for trade in response_data if trade['status'] in ['pending', 'reviewing', 'confirmed'])

                    writer.writerows(trades)

        except Exception as e:
            print(e)
