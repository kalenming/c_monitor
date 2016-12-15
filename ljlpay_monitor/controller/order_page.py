# -*- coding: utf-8 -*-
import sys
import datetime
import json
from flask_restful import reqparse
from flask import render_template, request

from ljlpay_monitor import app
from ljlpay_monitor.model.order import Model

from config.config import ec_alias_map
from config.config import businessAppId


"""
 * Created by ming on 16/11/10.
"""
reload(sys)
sys.setdefaultencoding('utf-8')
parser = reqparse.RequestParser()
parser.add_argument('user_id')


@app.route('/order_dashboard', methods=['GET', 'POST'])
def loan_monitor():
    """
    :return:
    """

    # now = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    now = datetime.datetime.now() + datetime.timedelta(days=1)
    last_day = now - datetime.timedelta(days=365)
    one_week_ago = now - datetime.timedelta(days=7)
    now_str = str(now)[:10]
    last_day_str = str(last_day)[:10]
    one_week_ago = str(one_week_ago)[:10]

    date_begin = request.args.get('begin', last_day_str, type=str)
    date_end = request.args.get('end', now_str, type=str)
    m = Model(date_begin, date_end, businessAppId)
    result = m.get_loan_page()


    return render_template('order_dashboard.html',
                           result = result
                           )
