import gate_api
from gate_api.exceptions import ApiException, GateApiException
import pytz
from datetime import datetime

from .csv_generator import generate_csv_file

GATE_API_URL = "https://api.gateio.ws/api/v4"


class GateIOApi():
    def __init__(self, input_dict):
        configuration = gate_api.Configuration(
            host = GATE_API_URL,
            key = input_dict.get('apikey'),
            secret = input_dict.get('apisecret')
        )
        api_client = gate_api.ApiClient(configuration)
        self.api_instance = gate_api.SpotApi(api_client)
        self.wallet_api_instance = gate_api.WalletApi(api_client)
        self.api_action = input_dict.get('apiaction')
        self.start_date = input_dict.get('start_date')
        self.end_date = input_dict.get('end_date')
        self.initiate_request()

    def initiate_request(self):
        if self.api_action == 'deposits':
            self.get_deposits()
        elif self.api_action == 'spottrades':
            self.get_spot_trades()
        elif self.api_action == 'withdrawals':
            self.get_withdrawals()
        else:
            pass

    def get_spot_trades(self, currency_pair: str = 'BTC_USDT', limit: int = 100):
        try:
            csv_header = ['Koinly Date', 'Pair', 'Side', 'Amount', 'Total', 'Fee Amount', 'Fee Currency', 'Order ID', 'Trade ID']

            # returns list[Trade]
            api_response = self.api_instance.list_trades(currency_pair=currency_pair, limit=limit)
    
            trades = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(trade.create_time), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                'Pair': trade.currency_pair,
                'Side': trade.side,
                #TODO: confirm number of decimal places
                'Amount': trade.amount,
                #TODO: confirm Total calculation
                'Total': float(trade.amount) * float(trade.price),
                'Fee Amount': trade.fee,
                'Fee Currency': trade.fee_currency,
                'Order ID': trade.order_id,
                'Trade ID': trade.id,
                } for trade in api_response)
            generate_csv_file('capital_spot_trades', trades, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_trades: %s\n" % e)


    def get_withdrawals(self, limit: int=100):
        csv_header = ['Koinly Date', 'Amount', 'Currency', 'Label', 'TxHash']

        try:
            # returns list[LedgerRecord]
            api_response = self.wallet_api_instance.list_withdrawals(limit=limit)  
            trades = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(trade.timestamp), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                'Amount': trade.amount,
                'Currency': trade.currency,
                #TODO: confirm we're picking the right field
                'Label': trade.memo,
                'TxHash': trade.txid
                } for trade in api_response)
            generate_csv_file('capital_withdrawals', trades, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_withdrawals: %s\n" % e)


    def get_deposits(self, limit:int=100):
        csv_header = ['Koinly Date', 'Amount', 'Currency', 'Label', 'TxHash']

        try:
            # returns list[LedgerRecord]
            api_response = self.wallet_api_instance.list_deposits(limit=limit)     
            trades = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(trade.timestamp), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                'Amount': trade.amount,
                'Currency': trade.currency,
                #TODO: confirm the field
                'Label': trade.memo,
                'TxHash': trade.txid
                } for trade in api_response)
            generate_csv_file('capital_deposits',trades, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_deposits: %s\n" % e)




