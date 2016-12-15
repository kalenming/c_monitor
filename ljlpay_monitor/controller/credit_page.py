# -*- coding: utf-8 -*-
import sys
import datetime
import json
from flask_restful import reqparse
from flask import render_template, request

from ljlpay_monitor import app
from ljlpay_monitor.model.credit import Model
from ljlpay_monitor.model.ec_credit import EC_Model

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
"""
 * Created by YA on 16/9/29.
"""

reload(sys)
sys.setdefaultencoding('utf-8')
parser = reqparse.RequestParser()
parser.add_argument('user_id')


@app.route('/', methods=['GET','POST'])
def home():
    return render_template('home_index.html')


@app.route('/detail/<user_id>', methods=['GET', 'POST'])
def detail(user_id):
    m = Model('', '')
    company_table,table1, table2, sys_purchase = m.detail_page(user_id)

    return render_template('credit_detail.html',
                           company_detail=company_table,
                           success_detail=table1,
                           features=table2,
                           sys_purchase=sys_purchase)


@app.route('/credit_total', methods=['GET', 'POST'])
def credit_page():
    """
     评分接口
    :return:
    """
    now = datetime.datetime.now() + datetime.timedelta(days=1)
    last_day = now - datetime.timedelta(days=365)
    one_week_ago = now - datetime.timedelta(days=7)
    now_str = str(now)[:10]
    last_day_str = str(last_day)[:10]
    one_week_ago = str(one_week_ago)[:10]

    date_begin = request.args.get('begin', last_day_str, type=str)
    date_end = request.args.get('end', now_str, type=str)

    m = Model(date_begin, date_end,)
    amount_dis_column,pass_total,month_data = m.credit_page()


    return render_template('credit_dashboard.html',
                           title='评分监控系统',
                           limit = amount_dis_column,
                           date_begin=date_begin,
                           date_end=date_end,
                           pass_total = pass_total,
                           month_data=month_data

                           )

@app.route('/detail_table', methods=['GET', 'POST'])
def detail_table():
    """
     授信/拒绝详情表
    :return:
    """

    #now = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    now = datetime.datetime.now() + datetime.timedelta(days=1)
    last_day = now - datetime.timedelta(days=365)
    one_week_ago = now - datetime.timedelta(days=7)
    now_str = str(now)[:10]
    last_day_str = str(last_day)[:10]
    one_week_ago = str(one_week_ago)[:10]

    date_begin = request.args.get('begin', last_day_str, type=str)
    date_end = request.args.get('end', now_str, type=str)

    m = Model(date_begin, date_end)
    success_detail,fail_detail = m.detail_list_page()

    return render_template('credit_detail_table.html',
                           title=' 评分监控系统',
                           success_detail=success_detail,
                           fail_detail=fail_detail,
                           date_begin=date_begin,
                           date_end=date_end)

@app.route('/e_commerce/<EC>', methods=['GET', 'POST'])
def ec_monitor(EC):
    now = datetime.datetime.now() + datetime.timedelta(days=1)
    last_day = now - datetime.timedelta(days=365)
    one_week_ago = now - datetime.timedelta(days=7)
    now_str = str(now)[:10]
    last_day_str = str(last_day)[:10]
    one_week_ago = str(one_week_ago)[:10]

    date_begin = request.args.get('begin', last_day_str, type=str)
    date_end = request.args.get('end', now_str, type=str)

    m = EC_Model(date_begin, date_end, EC)
    amount_dis_column, pass_total, month_data = m.credit_page()
    return render_template('credit_ec_dashboard.html',
                           title=' 评分监控系统',
                           EC = EC,
                           limit=amount_dis_column,
                           date_begin=date_begin,
                           date_end=date_end,
                           pass_total=pass_total,
                           month_data=month_data
                           )


@app.route('/ec_detail_table/<EC>', methods = ['GET','POST'])
def ec_detail_table(EC):
    """
     授信/拒绝详情表
    :return:
    """

    #now = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    now = datetime.datetime.now() + datetime.timedelta(days=1)
    last_day = now - datetime.timedelta(days=365)
    one_week_ago = now - datetime.timedelta(days=7)
    now_str = str(now)[:10]
    last_day_str = str(last_day)[:10]
    one_week_ago = str(one_week_ago)[:10]

    date_begin = request.args.get('begin', last_day_str, type=str)
    date_end = request.args.get('end', now_str, type=str)

    m = EC_Model(date_begin, date_end,EC)
    success_detail,fail_detail = m.get_ec_detail_result()
    return render_template('credit_ec_detail_table.html',
                           title=' 评分监控系统',
                           success_detail=success_detail,
                           fail_detail=fail_detail,
                           date_begin=date_begin,
                           date_end=date_end)

