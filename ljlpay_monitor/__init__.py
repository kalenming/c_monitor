# -*- coding: utf-8 -*-

"""
 * Created by YA on 16/9/30.
"""

from flask import Flask

app = Flask(__name__)
app.jinja_env.add_extension("chartkick.ext.charts")


from ljlpay_monitor.controller import credit_page
from ljlpay_monitor.controller import overdue_page
from ljlpay_monitor.controller import order_page
from ljlpay_monitor.controller import report_page




