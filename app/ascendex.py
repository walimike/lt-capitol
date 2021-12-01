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


class AscendexApi():
    def __init__(self, input_dict):
        print(f'input_dict: {input_dict}')
        self.apikey = input_dict.get('apikey')
        self.apisecret = str(input_dict.get('apisecret'))
        self.api_action = input_dict.get('apiaction')

        self.initiate_request()

    def initiate_request(self):
        if self.api_action == 'deposits':
            self.get_deposits_and_withdraws()
        elif self.api_action == 'withdraws':
            self.get_deposits_and_withdraws()
        elif self.api_action == 'spottrades':
            self.ascend_trades()

    def get_deposits_and_withdraws(self):
        DEPOSITS_WITHDRAWS_API_URL = "https://ascendex.com/api/pro/v1/wallet/transactions"

        timestamp  = int(time.time() * 1000)
        api_path = 'wallet/transactions'
        pre_hash_msg = f'{timestamp}+{api_path}'.encode('utf-8')

        hmac_sha256 = hmac.new(
            self.apisecret.encode('utf-8'),
            pre_hash_msg,
            hashlib.sha256).digest()

        signature = base64.b64encode(hmac_sha256).decode('utf-8')

        headers = {
            'x-auth-key': self.apikey,
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

            response = requests.get(DEPOSITS_WITHDRAWS_API_URL, params, headers=headers)
            response_content = json.loads(response.content)
            response_data = response_content['data'].get('data')

            if len(response_data) > 0:
                deposits_and_withdraws.extend(response_data)
                current_page+=1
            else:
                last_page_reached = True

        csv_header = ['Koinly Date', 'Amount', 'Currency', 'Label', 'TxHash']
        try:
            trades = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(trade['time']/1000), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                'Amount': trade['amount'],
                'Currency': trade['asset'],
                'Label': trade['status'],
                'TxHash': trade['requestId'],
                } for trade in deposits_and_withdraws if trade['status'] in ['pending', 'reviewing', 'confirmed'])
            generate_csv_file('ascendex_deposits_and_withdraws', trades, csv_header)
        except Exception as e:
            print(e)


    def ascend_trades(self):
        TRADES_API_URL = 'https://ascendex.com/api/pro/v2/order/hist'

        timestamp  = int(time.time() * 1000)
        api_path = 'order/hist'
        pre_hash_msg = bytearray(f'{timestamp}+{api_path}'.encode('utf-8'))

        hmac_sha256 = hmac.new(
            base64.b64decode(self.apisecret),
            pre_hash_msg,
            hashlib.sha256).digest()

        signature = base64.b64encode(hmac_sha256).decode('utf-8')

        headers = {
            'x-auth-key': self.apikey,
            'x-auth-timestamp': str(timestamp),
            'x-auth-signature': signature
        }
        print(f'headers: {headers}')

        # params = dict(
        #     symbol='ASD/USDT',
        #     limit=1000
        # )
        params = {"symbol": 'ASD/USDT', "limit": 1000}

        response = requests.get(TRADES_API_URL, params, headers=headers)
        print(f'response: {response.__dict__}')
        response_content = json.loads(response.content)
        response_data = response_content.get('data').get('data')
        print(dict(response_data[0]))

        csv_header = ['Koinly Date', 'Pair', 'Side', 'Amount', 'Total', 'Fee Amount', 'Fee Currency', 'Order ID', 'Trade ID']
        try:
            trades = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(trade['createTime'])/1000).strftime('%Y-%m-%d %H:%M'),
                'Pair': params['symbol'],
                #not sure which field it is
                'Side': trade['side'],
                #TODO: confirm if it's q which is trade size
                'Amount': trade['price'],
                #TODO: confirm Total calculation
                'Total': float(trade['price']) * float(trade['orderQty']),
                #TODO: not sure which field to pic
                'Fee Amount': trade['fee'],
                #TODO: not sure which field to pic
                'Fee Currency': trade['feeAsset'],
                'Order ID': trade['orderId'],
                #confirm
                'Trade ID': trade['seqNum'],
            } for trade in response_data)

            generate_csv_file('ascendex_trades', trades, csv_header)
        except Exception as e:
            print(e)
