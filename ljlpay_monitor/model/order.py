# -*- coding: utf-8 -*-

import json
import datetime
from ljlpay_monitor.db.mysql_rc_pool import db_trade
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


"""
 * Created by YA on 16/11/10.
"""


class Model(object):

    def __init__(self, date_begin, date_end, business_app_id):
        self.date_begin = date_begin
        self.date_end = date_end
        self.ec_id = business_app_id

    def get_loan_page(self):
        """
        :return:
        """
        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d')
        date_end = datetime.datetime.strptime(self.date_end, '%Y-%m-%d')

        # 1.总用户贷款数量、金额
        total_count, total_amount = self._get_count_amount(date_begin, date_end, self.ec_id)

        # 2.月贷款数量、金额趋势
        per_month_count, per_month_amount = self._get_month_tend(date_begin, date_end, self.ec_id)

        # 3.贷款额度相对频次分布
        amount_interval = 100
        loan_amount_dis = self._get_amount_dis(date_begin, date_end, self.ec_id, amount_interval)

        # 4.用户贷款总额度分布
        total_amount_interval = 1000
        total_amount_dis = self._get_total_amount_dis(date_begin, date_end, self.ec_id, total_amount_interval)

        # 5.授信时长与贷款总额度散点图
        loan_len_relation = self._get_loan_len_relation(self.ec_id,date_begin, date_end)

        result = {
             'total_count': total_count,  # 总贷款次数
             'total_amount': total_amount,  # 总贷款金额
             'per_month_count': per_month_count,  # 月贷款次数
             'per_month_amount': per_month_amount,  # 月贷款额度
             'loan_amount_dis': loan_amount_dis,  # 贷款金额分布
             'total_amount_dis': total_amount_dis,  # 用户贷款总金额分布
             'loan_len_relation': loan_len_relation  # 总贷款金额与授信时长关系
         }
        return result

    @staticmethod
    def _get_count_amount(date_begin, date_end, ec_id):
        sql = '''
            SELECT COUNT(id),SUM(loan_amount) FROM loan
            WHERE business_app_id = '%s'
            AND pay_time BETWEEN '%s' AND '%s'
        ''' % (ec_id, date_begin, date_end)
        logger.info('count_amount_sql: %s', sql)
        result = db_trade.query_one(sql)
        logger.info('count_amount_query_result: %s', result)
        if result and result[0] and result[1]:
            counts = int(result[0])  # 总贷款次数
            amount = round(result[1])  # 总贷款金额
        else:
            counts = 0
            amount = 0
        logger.info('total_counts: %s', counts)
        logger.info('total_amount: %s', amount)
        return counts, amount

    @staticmethod
    def _get_month_tend(date_begin, date_end, ec_id):
        sql = """
            SELECT DATE_FORMAT(pay_time, '%%Y/%%m') T, COUNT(id), SUM(loan_amount)
            FROM loan
            WHERE business_app_id = '%s'
            AND pay_time BETWEEN '%s' AND '%s' GROUP BY T ORDER BY T
        """ % (ec_id, date_begin, date_end)
        logger.info('month_tend_SQL: %s', sql)
        result = db_trade.query_all(sql)
        logger.info('month_tend_query_result: %s', result)

        if result and result[0][0] and result[0][1]:
            months = [row[0].encode('utf-8') for row in result]
            counts = [int(row[1]) for row in result]
            amount = [round(row[2]) for row in result]
        else:
            months = [0]
            counts = [0]
            amount = [0]
        logger.info('month_tend-countsList: %s', counts)
        logger.info('month_tend-monthsList: %s', months)
        logger.info('month_tend_amountList: %s', amount)

        # 月贷款次数趋势数据字典
        counts_tend = {
            'months': months,  # X轴月份
            'counts': counts  # Y轴计数
        }

        # 月贷款金额趋势数据字典
        amount_tend = {
            'months': months,
            'amount': amount
        }
        return counts_tend,amount_tend

    @staticmethod
    def _get_amount_dis(date_begin, date_end, ec_id, interval):
        sql = """
            SELECT loan_amount FROM loan
            WHERE business_app_id = '%s'
            AND pay_time BETWEEN '%s' AND '%s' order by loan_amount desc
        """ % (ec_id, date_begin, date_end)
        logger.info('amount_dis_SQL: %s', sql)
        result = db_trade.query_all(sql)
        logger.info('amount_dis_query_result: %s', result)
        # 给额度分布计数存入字典中
        amount_dis_dict = dict()
        if result :
            for row in result:
                amount = row[0] // interval  # 金额落入区间
                amount_dis_dict[int(amount)] = amount_dis_dict.get(int(amount), 0) + 1  # 字典中金额区间计数+1
        else:
            amount_dis_dict = {0: 0}

        logger.info('amount_distribution_dict: %s', amount_dis_dict)

        total = len(result)
        print total
        # 额度分布字典排序成键值对tuple list
        amount_dis_sorted = sorted(amount_dis_dict.iteritems(), key=lambda x: x[0], reverse=False)

        print amount_dis_sorted
        # 额度分布字典：排序后额度list+对应计数list
        distribution = {
            'amount_interval': [e[0]  for e in amount_dis_sorted],
            'amount_counts': [round(float(e[1])/float(total)*100,2) for e in amount_dis_sorted]
        }
        logger.info('single_loan_amount_distribution: %s', distribution)
        return distribution

    @staticmethod
    def _get_total_amount_dis(date_begin, date_end, ec_id, interval):
        sql = """
            SELECT SUM(loan_amount) FROM loan
            WHERE business_app_id = '%s'
            AND pay_time BETWEEN '%s' AND '%s'
            GROUP BY enterprise_id
        """ % (ec_id, date_begin, date_end)
        logger.info('total_amount_distribution_SQL: %s', sql)
        result = db_trade.query_all(sql)
        logger.info('total_amount_distribution_query_result: %s', result)


        total_loan_dis_dict = dict()
        if result and result[0] and result[0][0]:
            for row in result:
                total_loan = row[0] // interval  # 用户贷款总金额落入区间
                total_loan_dis_dict[int(total_loan)] = total_loan_dis_dict.get(int(total_loan), 0) + 1
        else:
            total_loan_dis_dict = {0: 0}
        # 总贷款额度排序成键值tuple list
        total_loan_sorted = sorted(total_loan_dis_dict.iteritems(), key=lambda x: x[0], reverse=False)

        # 总贷款额度分布字典：排序后额度list+对应计数list
        total= len(result)
        distribution = {
            'amount_interval': [e[0] for e in total_loan_sorted],
            'amount_counts': [round(float(e[1])/float(total)*100,2) for e in total_loan_sorted]
        }
        logger.info('total_loan_amount_distribution: %s', distribution)

        return distribution

    @staticmethod
    def _get_loan_len_relation(ec_id,date_begin,date_end):
        sql = """
            SELECT C.add_time,
            SUM(CASE WHEN L.loan_amount IS NOT NULL THEN L.loan_amount ELSE 0 END)
            FROM credit C
            left JOIN loan L ON C.enterprise_id = L.enterprise_id
            WHERE business_app_id = '%s' and
             C.add_time BETWEEN '%s' AND '%s'
            GROUP BY C.enterprise_id ORDER BY C.add_time DESC
        """ % (ec_id,date_begin, date_end)
        logger.info('loan_timeLength_relation_SQL: %s', sql)
        result = db_trade.query_all(sql)
        logger.info('loan_timeLength_relation_query_result: %s', result)

        if result and result[0] and result[0][0]:  # 判断查询结果是否为空
            c_day = datetime.datetime.now()

            time_length_list = [(c_day-row[0]).days for row in result]
            loan_amount_list = [int(row[1]) for row in result]
        else:
            time_length_list = [0]
            loan_amount_list = [0]
        logger.info('使用时间长度列表:%s', time_length_list)
        logger.info('贷款总金额列表: %s', loan_amount_list)

        # 用户授信时长与贷款总金额关系字典
        len_loan_relation = {
            'time_length': time_length_list,
            'loan_amount': loan_amount_list
        }

        return len_loan_relation

