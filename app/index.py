from app import app
from flask import  render_template, request

from .ascendex import ascendexApiCall
from .bithumb import bithumbApiCall
from .ftexchange import ftexchangeApiCall
from .gate_io import gateIoApiCall

def handle_post_request(trade_api, apikey, apisecret):
    if trade_api == 'gateio':
        gateIoApiCall(apikey, apisecret)
    elif trade_api == 'ascendex':
        ascendexApiCall(apikey, apisecret)
    elif trade_api == 'ftxapi':
        ftexchangeApiCall(apikey, apisecret)
    elif trade_api == 'bithumb':
        bithumbApiCall(apikey, apisecret)
    else:
        raise AttributeError

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/handle_data', methods=['POST'])
def handle_data():
    trade_api = request.form['tradeapi']
    apikey=request.form['apikey']
    apisecret=request.form['apisecret']
    handle_post_request(trade_api, apikey, apisecret)
    return render_template('index.html')
    #trade api options => gateio, ascendex, ftxapi, bithumb


