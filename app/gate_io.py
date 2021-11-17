import gate_api
from gate_api.exceptions import ApiException, GateApiException
import csv
import pytz
from datetime import datetime


GATE_API_URL = "https://api.gateio.ws/api/v4"

def gateIoApiCall(api_key, api_secret):
    gate_io = GateIOApi(api_key, api_secret)
    gate_io.get_spot_trades()
    gate_io.get_withdrawals()
    gate_io.get_deposits()


class GateIOApi():
    def __init__(self, api_key, api_secret):
        configuration = gate_api.Configuration(
            host = GATE_API_URL,
            key = api_key,
            secret = api_secret
        )
        api_client = gate_api.ApiClient(configuration)
        self.api_instance = gate_api.SpotApi(api_client)
        self.wallet_api_instance = gate_api.WalletApi(api_client)


    def get_spot_trades(self, currency_pair: str = 'BTC_USDT', limit: int = 100):
        try:
            csv_header = ['Koinly Date', 'Pair', 'Side', 'Amount', 'Total', 'Fee Amount', 'Fee Currency', 'Order ID', 'Trade ID']

            # returns list[Trade]
            api_response = self.api_instance.list_trades(currency_pair=currency_pair, limit=limit)

            with open('capital_spot_trades.csv', 'w', encoding='UTF8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_header)
                writer.writeheader()
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

                writer.writerows(trades)

        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_trades: %s\n" % e)


    def get_withdrawals(self, limit: int=100):
        csv_header = ['Koinly Date', 'Amount', 'Currency', 'Label', 'TxHash']

        try:
            # returns list[LedgerRecord]
            api_response = self.wallet_api_instance.list_withdrawals(limit=limit)

            with open('capital_withdrawals.csv', 'w', encoding='UTF8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_header)
                writer.writeheader()
                trades = ({
                    #TODO: confirm if create_time is in seconds
                    'Koinly Date': datetime.fromtimestamp(int(trade.timestamp), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                    'Amount': trade.amount,
                    'Currency': trade.currency,
                    #TODO: confirm we're picking the right field
                    'Label': trade.memo,
                    'TxHash': trade.txid
                    } for trade in api_response)

                writer.writerows(trades)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_withdrawals: %s\n" % e)


    def get_deposits(self, limit:int=100):
        csv_header = ['Koinly Date', 'Amount', 'Currency', 'Label', 'TxHash']

        try:
            # returns list[LedgerRecord]
            api_response = self.wallet_api_instance.list_deposits(limit=limit)

            with open('capital_deposits.csv', 'w', encoding='UTF8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_header)
                writer.writeheader()
                trades = ({
                    #TODO: confirm if create_time is in seconds
                    'Koinly Date': datetime.fromtimestamp(int(trade.timestamp), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                    'Amount': trade.amount,
                    'Currency': trade.currency,
                    #TODO: confirm the field
                    'Label': trade.memo,
                    'TxHash': trade.txid
                    } for trade in api_response)

                writer.writerows(trades)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_deposits: %s\n" % e)




