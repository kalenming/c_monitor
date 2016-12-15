import sys
import datetime
import json
from flask_restful import reqparse
from flask import render_template, request
from ljlpay_monitor.model.report import Report
from ljlpay_monitor import app

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)








@app.route('/report/daily')
def report_daily():
    r = Report()
    daily = r.daily_report()
    return render_template('report_daily.html', daily=daily)


@app.route('/report/week')
def report_weekly():
    r = Report()
    daily = r.week_report()
    return render_template('report_weekly.html', daily=daily)
