# -*- coding: utf-8 -*-
import json
import datetime
import operator
from ljlpay_monitor.db.mysql_rc_pool import db_rc,db_trade



"""
 * Created by YA on 16/9/30.
"""


class ALERT_Model(object):

    @staticmethod
    def get_alert(timeout):

        business_app_id = 'BUS_2016090511360432647530'
        now = datetime.datetime.now() + datetime.timedelta(days=1)
        alert_start = datetime.datetime(now.year,now.month,now.day,0,0,0)
        alert_start_str = str(alert_start)[0:19]
        alert3 =alert_start + datetime.timedelta(days=3)
        alert3_str = str(alert3)[0:19]
        alert7 = alert_start + datetime.timedelta(days=7)
        alert7_str = str(alert7)[0:19]

        sql = '''select id,loan_user_name,loan_amount,overdue_time
            from loan where business_app_id = '%s'
            ''' % (business_app_id)

        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(sql)
        data = cursor_trade.fetchall()
        cursor_trade.close()
        conn_trade.close()

        table_data = list()
        if int(timeout) == 3:
            if data and len(data) > 0:
                for i in data:
                    alert_days = (i[3]-alert_start).days + 1

                    if str(i[3]) > alert_start_str and str(i[3]) < alert3_str:

                        inner_data = dict()
                        inner_data['id'] = int(i[0])
                        inner_data['loan_user_name'] = str(i[1])
                        inner_data['loan_amount'] = i[2]
                        inner_data['overdue_time'] = str(i[3])[0:10]
                        inner_data['overdue_timeout'] = alert_days
                        table_data.append(inner_data)
        if int(timeout) == 7:
            if data and len(data) > 0:
                for i in data:
                    alert_days = (i[3] - alert_start).days + 1
                    if str(i[3]) > alert3_str and str(i[3]) < alert7_str:
                        inner_data = dict()
                        inner_data['id'] = int(i[0])
                        inner_data['loan_user_name'] = str(i[1])
                        inner_data['loan_amount'] = i[2]
                        inner_data['overdue_time'] = str(i[3])[0:10]
                        inner_data['overdue_timeout'] = alert_days
                        table_data.append(inner_data)

        return table_data


