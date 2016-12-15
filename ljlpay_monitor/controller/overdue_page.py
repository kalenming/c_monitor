# -*- coding: utf-8 -*-
import sys
import datetime
import json
from flask_restful import reqparse
from flask import render_template, request
from ljlpay_monitor import app
from ljlpay_monitor.model.overdue import Model
from ljlpay_monitor.model.ec_overdue import EC_Model
from ljlpay_monitor.model.overdue_alert import ALERT_Model

"""
 * Created by ming on 16/11/7.
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
reload(sys)
sys.setdefaultencoding('utf-8')
parser = reqparse.RequestParser()
parser.add_argument('user_id')



@app.route('/overdue_detail/<user_id>', methods=['GET', 'POST'])
def overdue_detail(user_id):
    m = Model('', '')
    company_table,credit_table = m.detail_page(user_id)
    return render_template('overdue_detail.html',
                           company_detail=company_table,
                           credit_detail = credit_table
                           )


@app.route('/overdue_dashboard', methods=['GET', 'POST'])
def overdue_monitor():
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

    m = Model(date_begin, date_end)
    unpay_payed_count,amount_dis_column,month_data = m.overdue_page()

    return render_template('overdue_dashboard.html',
                           title=' 评分监控系统',
                           unpay_or_payed=unpay_payed_count,
                           limit=amount_dis_column,
                           date_begin=date_begin,
                           date_end=date_end,
                           month_data = month_data
                           )



@app.route('/overdue_detail_table', methods=['GET', 'POST'])
def overdue_detail_table():
    """
     逾期未还/已还详情表
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
    unpay_detail,payed_detail = m.detail_list_page()

    return render_template('overdue_detail_table.html',
                           title=' 评分监控系统',
                           unpay_detail=unpay_detail,
                           payed_detail=payed_detail,
                           date_begin=date_begin,
                           date_end=date_end)
@app.route('/overdue_e_commerce/<EC>', methods=['GET', 'POST'])
def overdue_ec_monitor(EC):
    now = datetime.datetime.now() + datetime.timedelta(days=1)
    last_day = now - datetime.timedelta(days=365)
    one_week_ago = now - datetime.timedelta(days=7)
    now_str = str(now)[:10]
    last_day_str = str(last_day)[:10]
    one_week_ago = str(one_week_ago)[:10]

    date_begin = request.args.get('begin', last_day_str, type=str)
    date_end = request.args.get('end', now_str, type=str)

    m = EC_Model(date_begin, date_end, EC)
    unpay_payed_count, amount_dis_column, month_data = m.overdue_page()


    return render_template('overdue_ec_dashboard.html',
                           title=' 评分监控系统',
                           EC = EC,
                           unpay_or_payed=unpay_payed_count,
                           limit =amount_dis_column,
                           date_begin=date_begin,
                           date_end=date_end,
                           month_data = month_data

                           )

@app.route('/overdue_ec_detail_table/<EC>', methods = ['GET','POST'])
def overdue_ec_detail_table(EC):
    """
     逾期未还/已还详情表
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
    unpay_payed_count, amount_dis_column, month_data = m.overdue_page()
    return render_template('overdue_ec_detail_table.html',
                            title=' 评分监控系统',
                            unpay_or_payed=unpay_payed_count,
                            limit=amount_dis_column,
                            date_begin=date_begin,
                            date_end=date_end,
                            month_data=month_data)



@app.route('/overdue_alert_table/<timeout>', methods=['GET', 'POST'])
def overdue_alert_table(timeout):
    """
     逾期提醒
    :return:
    """

    m = ALERT_Model()
    alert_detail = m.get_alert(timeout)


    return render_template('overdue_alert_table.html',
                           title=' 评分监控系统',
                           alert_detail=alert_detail
                           )