import gate_api

import gate_api
from gate_api.exceptions import ApiException, GateApiException

# Defining the host is optional and defaults to https://api.gateio.ws/api/v4
# See configuration.py for a list of all supported configuration parameters.
configuration = gate_api.Configuration(
    host = "https://api.gateio.ws/api/v4"
)


api_client = gate_api.ApiClient(configuration)
# Create an instance of the API class
api_instance = gate_api.DeliveryApi(api_client)
settle = 'usdt' # str | Settle currency

gate_deposit_api = gate_api.WalletApi(api_client)
currency = 'BTC' # str | Filter by currency. Return all currency records if not specified (optional)
_from = 1602120000 # int | Time range beginning, default to 7 days before current time (optional)
to = 1602123600 # int | Time range ending, default to current time (optional)
limit = 100 # int | Maximum number of records to be returned in a single list (optional) (default to 100)
offset = 0 # int | List offset, starting from 0 (optional) (default to 0)


def gateIoApiCall(apikey, apisecret):
    pass



class GateIOApi():
    def __init__(self):
        pass

    def retreive_deposit(self):
        try:
            # Retrieve deposit records
            import pdb;
            pdb.set_trace()
            api_response = gate_deposit_api.list_deposits(currency=currency, _from=_from, to=to, limit=limit, offset=offset)
            print('++++++++++> deposits', api_response)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_deposits: %s\n" % e)

    def retreive_withdrawal(self):
        api_client = gate_api.ApiClient(configuration)
        # Create an instance of the API class
        api_instance = gate_api.WalletApi(api_client)
        currency = 'BTC' # str | Retrieve data of the specified currency (optional)
        try:
            # Retrieve withdrawal status
            api_response = api_instance.list_withdraw_status(currency=currency)
            print(api_response)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling WalletApi->list_withdraw_status: %s\n" % e)

    def get_api_lists(self):
        try:
            # List all futures contracts
            # api_response = api_instance.list_delivery_contracts(settle)
            import pdb;
            pdb.set_trace()
            api_response = gate_deposit_api.list_deposits(currency=currency, _from=_from, to=to, limit=limit, offset=offset)
            print('++++++++++> deposits', api_response)
            # print('=========>',api_response)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling DeliveryApi->list_delivery_contracts: %s\n" % e)

