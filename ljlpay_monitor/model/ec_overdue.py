# -*- coding: utf-8 -*-
import json
import datetime
import operator
from ljlpay_monitor.db.mysql_rc_pool import db_rc,db_trade
import logging
from config.config import  ec_alias_map



"""
 * Created by YA on 16/9/30.
"""


class EC_Model(object):
    def __init__(self, date_begin, date_end,EC):
        self.date_begin = date_begin
        self.date_end = date_end

        self.businessAppId = ec_alias_map[EC]

    def overdue_page(self):
        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d')

        date_end = datetime.datetime.strptime(self.date_end, '%Y-%m-%d')

        businessAppId = self.businessAppId

        # 1.获取逾期用户数量情况

        unpay_payed_count = self._get_overdue_unpay_payed_count(date_begin, date_end,businessAppId)

        # 2.额度分布

        amount_dis_column = self._get_overdue_distribution(date_begin, date_end, businessAppId)

        # 3. 按月汇总逾期未还金额，逾期未还用户，逾期已还用户
        month_data = self.get_overdue_month(date_begin, date_end)

        return unpay_payed_count,amount_dis_column,month_data

    def detail_list_page(self):
        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d')
        date_end = datetime.datetime.strptime(self.date_end, '%Y-%m-%d')
        # 3.获取逾期未还的详成功情况

        businessAppId = self.businessAppId
        unpay_detail = self._get_unpay_detail(date_begin, date_end,businessAppId)

        # 4.获取逾期已还用户
        payed_detail = self._get_payed_detail(date_begin, date_end,businessAppId)

        return unpay_detail, payed_detail

    def detail_page(self, user_id):
        user_id = user_id
        company_detail,credit_detail = self._get_user_detail(user_id)
        return company_detail,credit_detail



    @staticmethod
    def _get_payed_detail(date_begin, date_end,businessAppId):
        sql = '''select enterprise_id ,loan_user_name,loan_amount,overdue_time from loan
                        where  state = 9 and overdue_time between  '%s' and '%s'
                        and business_app_id= '%s' ''' % (date_begin, date_end, businessAppId)
        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()

        cursor_trade.execute(sql)
        payed_result = cursor_trade.fetchone()
        cursor_trade.close()
        conn_trade.close()

        table_data = list()

        if payed_result and len(payed_result) > 0:
            for i in payed_result:
                inner_data = dict()
                inner_data['enterprise_id'] = int(i[0])
                inner_data['loan_user_name'] = str(i[1])
                inner_data['loan_amount'] = i[2]
                inner_data['overdue_time'] = str(i[3])[0:10]
                inner_data['overdue_timeout'] = (date_end-i[3]).days

                table_data.append(inner_data)

        return table_data

    @staticmethod
    def _get_user_detail(user_id):

        sql = '''select enterprise_id ,loan_user_name,loan_amount,overdue_time from loan
                where  state = 8 and enterprise_id = '%s' ''' % (user_id)

        now = datetime.datetime.now() + datetime.timedelta(days=1)

        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(sql)
        result = cursor_trade.fetchall()
        cursor_trade.close()
        conn_trade.close()
        check_pass_table = list()

        table_data = list()

        if result and len(result) > 0:
            for i in result:
                inner_data = dict()
                inner_data['enterprise_id'] = int(i[0])
                inner_data['loan_user_name'] = str(i[1])
                inner_data['loan_amount'] = i[2]
                inner_data['overdue_time'] = str(i[3])[0:10]
                inner_data['overdue_timeout'] = (now - i[3]).days

                table_data.append(inner_data)

        return table_data

    @staticmethod
    def _get_unpay_detail(date_begin, date_end,businessAppId):
        sql = '''select enterprise_id ,loan_user_name,loan_amount,overdue_time from loan
                where  state = 8 and overdue_time between  '%s' and '%s'
                and business_app_id= '%s' ''' % (date_begin, date_end, businessAppId)
        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()

        cursor_trade.execute(sql)
        unpay_result = cursor_trade.fetchone()
        cursor_trade.close()
        conn_trade.close()

        table_data = list()

        if unpay_result and len(unpay_result) > 0:
            for i in unpay_result:
                user_detail = dict()
                user_detail['enterprise_id'] = int(i[0])
                user_detail['loan_user_name'] = str(i[1])
                user_detail['loan_amount'] = float(i[2])
                user_detail['overdue_time'] = str(i[3])[0:10]
                user_detail['overdue_timeout'] = (date_end-i[3]).days
                table_data.append(user_detail)

        return table_data


    @staticmethod
    def _get_overdue_unpay_payed_count(date_begin, date_end,businessAppId):
        sql1 = '''select count(id),sum(loan_amount)  from loan
        where  state = 8 and overdue_time between  '%s' and '%s'
        and business_app_id= '%s' ''' % (date_begin, date_end,businessAppId)

        sql2 = '''select count(id) ,sum(loan_amount) from loan
        where state = 9 and overdue_time between  '%s' and '%s'
                and business_app_id= '%s' ''' % (date_begin, date_end,businessAppId)
        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(sql1)
        unpay_result = cursor_trade.fetchone()
        cursor_trade.execute(sql2)
        payed_result = cursor_trade.fetchone()
        cursor_trade.close()
        conn_trade.close()



        inner_data = {
            'unpay': unpay_result,
            'payed': payed_result
        }
        print inner_data
        return inner_data





    def get_overdue_month(date_begin,date_end,businessAppId):
        # 按月统计逾期情况

        sql = '''SELECT DATE_FORMAT(overdue_time,"%%Y-%%m") as month,
        SUM(DISTINCT( CASE WHEN state=8 THEN loan_amount ELSE 0 END) ) ,
        SUM(DISTINCT( CASE WHEN state=9 THEN loan_amount ELSE 0 END) ) ,
        COUNT(DISTINCT( CASE WHEN state=8 THEN id ELSE 0 END)) ,
        COUNT(DISTINCT( CASE WHEN state=9 THEN id ELSE 0 END))
        FROM loan
        WHERE    overdue_time between '%s' AND '%s'
        and business_app_id= '%s'
        GROUP BY month order by month
        ''' % (date_begin, date_end,businessAppId)
        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(sql)
        result = cursor_trade.fetchall()
        cursor_trade.close()
        conn_trade.close()

        month_unpay_amount = list()
        month_payed_amount = list()
        month_unpay_count = list()
        month_payed_count = list()
        month = list()

        for row in result:
            month.append(str(row[0]))
            month_unpay_amount.append(float(row[1]))
            month_payed_amount.append(float(row[2]))
            month_unpay_count.append(row[3])
            month_payed_count.append(row[4])

        month_data = {
            'months' :month,
            'unpay_amount':month_unpay_amount,
            'payed_amount':month_payed_amount,
            'unpay_count':month_unpay_count,
            'payed_count':month_payed_count
        }

        return  month_data



    @staticmethod
    def _get_overdue_distribution(date_begin,date_end,businessAppId):
        sql = '''select loan_amount
            from loan
            where   overdue_time between  '%s' and '%s'
            and business_app_id= '%s' ''' % (date_begin, date_end,businessAppId)

        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(sql)
        result = cursor_trade.fetchall()
        cursor_trade.close()
        conn_trade.close()


        unpay_count = list()
        payed_count = list()
        limit = [range(0, 1), range(1, 2), range(2, 3), range(3, 4), range(4, 5)]
        for column in limit:
            unpay = 0
            payed = 0
            for row in result:
                if row[0] // 1000  in column:
                    unpay += 1
                if row[0] // 1000 in column:
                    payed += 1
            unpay_count.append(unpay)
            payed_count.append(payed)

        unpay = 0
        payed = 0
        for row in result :
            if row[0] // 1000 in column:
                unpay += 1
            if row[0] // 1000 in column:
                payed += 1
        unpay_count.append(unpay)
        payed_count.append(payed)
        overdue_amount = {
            'unpay':unpay_count,
            'payed':payed_count
        }
        return overdue_amount


