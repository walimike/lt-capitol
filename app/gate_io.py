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
        #TODO one action for deposits and withdraws
        if self.api_action == 'deposits':
            self.get_deposits_and_withdrawals()
        elif self.api_action == 'spottrades':
            self.get_spot_trades()
        elif self.api_action == 'withdrawals':
            self.get_deposits_and_withdrawals()
        else:
            pass

    def get_spot_trades(self):
        try:
            csv_header = ['Koinly Date', 'Pair', 'Side', 'Amount', 'Total', 'Fee Amount', 'Fee Currency', 'Order ID', 'Trade ID']

            my_trades = []
            for currency_pair in list(self.get_currency_pairs()):
                # returns list[Trade]
                current_page = 1
                last_page_reached = False
                while last_page_reached == False:
                    api_response = self.api_instance.list_my_trades(currency_pair=currency_pair, limit=1000, page=current_page)
                    if len(api_response) > 0:
                        my_trades.extend(api_response)
                        current_page+=1
                    else:
                        last_page_reached = True

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
                } for trade in my_trades)
            generate_csv_file('capital_spot_trades', trades, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_trades: %s\n" % e)


    def get_deposits_and_withdrawals(self):
        deposits_and_withdrawals = []
        deposits_and_withdrawals.extend(list(self.get_withdrawals()))
        deposits_and_withdrawals.extend(list(self.get_deposits()))

        csv_header = ['Koinly Date', 'Amount', 'Currency', 'Label', 'TxHash']
        generate_csv_file('capital_deposits_and_withdrawals', deposits_and_withdrawals, csv_header)

    def get_withdrawals(self):
        try:
            # returns list[LedgerRecord]
            withdrawals = []
            current_page = 1
            last_page_reached = False
            while last_page_reached == False:
                api_response = self.wallet_api_instance.list_withdrawals(limit=1000, page=current_page)
                if len(api_response) > 0:
                    withdrawals.extend(api_response)
                    current_page+=1
                else:
                    last_page_reached = True
            my_withdrawals = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(withdraw.timestamp), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                'Amount': withdraw.amount,
                'Currency': withdraw.currency,
                #TODO: confirm we're picking the right field
                'Label': withdraw.memo,
                'TxHash': withdraw.txid
                } for withdraw in withdrawals)
            return my_withdrawals
            # generate_csv_file('capital_withdrawals', withdrawls, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_withdrawals: %s\n" % e)


    def get_deposits(self):
        try:
            deposits = []
            current_page = 1
            last_page_reached = False
            while last_page_reached == False:
                # returns list[LedgerRecord]
                api_response = self.wallet_api_instance.list_deposits(limit=1000, page=current_page)
                if len(api_response) > 0:
                    deposits.extend(api_response)
                    current_page+=1
                else:
                    last_page_reached = True
            my_deposits = ({
                #TODO: confirm if create_time is in seconds
                'Koinly Date': datetime.fromtimestamp(int(deposit.timestamp), pytz.UTC).strftime('%Y-%m-%d %H:%M'),
                'Amount': deposit.amount,
                'Currency': deposit.currency,
                #TODO: confirm the field
                'Label': deposit.memo,
                'TxHash': deposit.txid
                } for deposit in deposits)
            return my_deposits
            # generate_csv_file('capital_deposits',my_deposits, csv_header)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_deposits: %s\n" % e)


    def get_currency_pairs(self):
        try:
            # List all currency pairs supported
            api_response = self.api_instance.list_currency_pairs()
            return (currency_pair.id for currency_pair in api_response)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_currency_pairs: %s\n" % e)



