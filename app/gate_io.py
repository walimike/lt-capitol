import gate_api
from gate_api.exceptions import ApiException, GateApiException
import pytz
from datetime import datetime
import requests
import time
import hashlib
import hmac

from .csv_generator import generate_csv_file, create_timestamp

GATE_API_URL = "https://api.gateio.ws/api/v4"


class GateIOApi():
    def __init__(self, input_dict):
        print(f'kwargs:: {input_dict}')
        configuration = gate_api.Configuration(
            host = GATE_API_URL,
            key = input_dict.get('apikey'),
            secret = input_dict.get('apisecret')
        )
        api_client = gate_api.ApiClient(configuration)
        self.api_instance = gate_api.SpotApi(api_client)
        self.wallet_api_instance = gate_api.WalletApi(api_client)
        self.api_action = input_dict.get('apiaction')
        self.key = input_dict.get('apikey')
        self.secret = input_dict.get('apisecret')
        self.start_date = create_timestamp(
                            input_dict.get('start_date')
                        )
        self.end_date = create_timestamp(
                            input_dict.get('end_date')
                        )
        self.initiate_request()

    def initiate_request(self):
        #TODO one action for deposits and withdraws
        if self.api_action == 'deposits':
            self.get_deposits_and_withdrawals()
        elif self.api_action == 'spottrades':
            self.get_spot_trades()
        elif self.api_action == 'withdrawals':
            self.get_deposits_and_withdrawals()
        else:
            pass

    def gen_sign(self, method, url, query_string=None, payload_string=None):
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(self.secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': self.key, 'Timestamp': str(t), 'SIGN': sign}

    def get_spot_trades(self):
        try:
            csv_header = ['Koinly Date', 'Pair', 'Side', 'Amount', 'Total', 'Fee Amount', 'Fee Currency', 'Order ID', 'Trade ID']

            host = "https://api.gateio.ws"
            prefix = "/api/v4"
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

            url = '/spot/my_trades'
            query_param = f'limit=1000&_from={self.start_date}&to={self.end_date}'
            sign_headers = self.gen_sign('GET', prefix + url, query_param)
            headers.update(sign_headers)
            r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers)

            trades = ({
                'Koinly Date': datetime.fromtimestamp(int(trade.get('create_time')), pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
                'Pair': trade.get('currency_pair'),
                'Side': trade.get('side'),
                'Amount': trade.get('amount'),
                'Total': float(trade.get('amount')) * float(trade.get('price')),
                'Fee Amount': trade.get('fee'),
                'Fee Currency': trade.get('fee_currency'),
                'Order ID': trade.get('order_id'),
                'Trade ID': trade.get('id'),
                } for trade in r.json())
            generate_csv_file('capital_spot_trades', trades, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_trades: %s\n" % e)


    def get_deposits_and_withdrawals(self):
        deposits_and_withdrawals = []
        deposits_and_withdrawals.extend(list(self.get_withdrawals()))
        deposits_and_withdrawals.extend(list(self.get_deposits()))

        csv_header = ['Koinly Date', 'Amount', 'Currency', 'Label', 'Description', 'TxHash']
        generate_csv_file('capital_deposits_and_withdrawals', deposits_and_withdrawals, csv_header)

    def get_withdrawals(self):
        try:
            # returns list[LedgerRecord]
            api_response = self.wallet_api_instance.list_withdrawals(limit=1000)
            my_withdrawals = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(withdraw.timestamp), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                'Amount': withdraw.amount,
                'Currency': withdraw.currency,
                #TODO: confirm we're picking the right field
                'Label': withdraw.memo,
                'Description': withdraw.memo,
                'TxHash': withdraw.txid
                } for withdraw in api_response)
            return my_withdrawals
            # generate_csv_file('capital_withdrawals', withdrawls, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_withdrawals: %s\n" % e)


    def get_deposits(self):
        try:
            api_response = self.wallet_api_instance.list_deposits(limit=1000)
            my_deposits = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(deposit.timestamp), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                'Amount': deposit.amount,
                'Currency': deposit.currency,
                #TODO: confirm the field
                'Label': '',
                'Description': deposit.memo,
                'TxHash': deposit.txid
                } for deposit in api_response)
            return my_deposits
            # generate_csv_file('capital_deposits',my_deposits, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_deposits: %s\n" % e)
