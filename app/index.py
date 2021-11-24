from app import app
from flask import  render_template, request, Response, flash, redirect

from .ascendex import AscendexApi
from .bithumb import BithumbGlobalRestAPI
from .ftexchange import FtxClient
from .gate_io import GateIOApi

def handle_post_request(**kwargs):
    try:
        if kwargs.get('trade_api') == 'gateio':
            GateIOApi(kwargs)
        elif kwargs.get('trade_api')== 'ascendex':
            AscendexApi(kwargs)
        elif kwargs.get('trade_api')== 'ftxapi':
            FtxClient(kwargs)
        elif kwargs.get('trade_api') == 'bithumb':
            BithumbGlobalRestAPI(kwargs)
    except Exception as e:
        flash(e.__str__())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/handle_data', methods=['POST'])
def handle_data():
    handle_post_request(
        trade_api=request.form['tradeapi'],
        apikey=request.form['apikey'],
        apisecret=request.form['apisecret'],
        apiaction=request.form['apiaction'],
        start_date=request.form['datefrom'],
        end_date=request.form['dateto']
    )
    from .csv_generator import csv_file
    if csv_file:
        file = open(csv_file)
        content = f'attachment; filename={csv_file}'
        return Response(
            file,
            mimetype="text/csv",
            headers={"Content-disposition": content})
    else:
        flash('An error occured with the data you provided')
    return render_template('index.html')
