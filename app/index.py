from app import app
from flask import  render_template, request, Response, stream_with_context, flash

from .ascendex import ascendexApiCall
from .bithumb import bithumbApiCall
from .ftexchange import FtxClient
from .gate_io import GateIOApi

def handle_post_request(**kwargs):
    try:
        if kwargs.get('trade_api') == 'gateio':
            GateIOApi(kwargs)
        elif kwargs.get('trade_api')== 'ascendex':
            ascendexApiCall(kwargs)
        elif kwargs.get('trade_api')== 'ftxapi':
            FtxClient(kwargs)
        elif kwargs.get('trade_api') == 'bithumb':
            bithumbApiCall(kwargs)
    except:
        pass

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
        return Response(
            stream_with_context(file),
            mimetype='text/csv', 
            headers={"Content-disposition":
                    f'"attachment; filename={csv_file}"'}
        )
    else:
        flash('An error occured with the data you provided')
    return render_template('index.html')
