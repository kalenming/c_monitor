# -*- coding: utf-8 -*-
import json
import datetime
from config.config import businessAppId
from ljlpay_monitor.db.mysql_rc_pool import db_trade,db_rc

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Model(object):
    def __init__(self, date_begin, date_end):

        self.date_begin = date_begin
        self.date_end = date_end
        self.businessAppId = businessAppId

    # 按页面划分减少查询时间

    def credit_page(self):

        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d')
        date_end = datetime.datetime.strptime(self.date_end, '%Y-%m-%d')
        businessAppId = self.businessAppId

        # 2.额度分布
        amount_dis_column = self._get_credit_distribution1(date_begin, date_end,businessAppId)

        #3.通过汇总
        pass_total = self._get_pass_total(date_begin, date_end, businessAppId)

        #4 按月汇总授信金额，通过用户，拒绝用户
        month_data = self.get_credit_month(date_begin, date_end, businessAppId)


        return amount_dis_column,pass_total,month_data


    def detail_list_page(self):
        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d')
        date_end = datetime.datetime.strptime(self.date_end, '%Y-%m-%d')
        businessAppId = self.businessAppId
        #1获取通过用户
        success_detail = self._get_check_pass_table(date_begin,date_end,businessAppId)
        #2获取失败用户
        fail_detail = self._get_check_reject_table(date_begin,date_end,businessAppId)

        return success_detail,fail_detail

    def detail_page(self,user_id):
        #1.获取授信用户详情
        user_id = user_id
        company_table, table1, table2, sys_purchase = self._get_user_detail(user_id)
        return company_table, table1, table2, sys_purchase


    @staticmethod
    def _get_user_detail(user_id):

        sql = '''select score, credit_grade, suggest_credit_amount, state, features,rules from risk_assessment_result
                  where version = 0 and enterprise_id = %s ''' % user_id
        sql1 = ''' SELECT period_static FROM zc_history_static WHERE version = 0 AND enterprise_id= %s''' % user_id

        # 查询企业详细信息
        sql2 = ''' SELECT  companyName,businessAddress, businessName, legalPerson, legalPersonPhone, contactPhone, regCapital, registrationDate
                    FROM enterprise WHERE version !=1 AND enterpriseId = %s ''' % user_id
        conn_rc = db_rc.get_conn_rc()
        cursor_rc = conn_rc.cursor()
        cursor_rc.execute(sql)
        data = cursor_rc.fetchone()

        cursor_rc.execute(sql1)
        period_data = cursor_rc.fetchone()
        cursor_rc.execute(sql2)
        company_data = cursor_rc.fetchone()
        cursor_rc.close()
        conn_rc.close()
        inner_data = dict()
        features = dict()
        synthesis_purchase = dict()
        company_table = dict()

        if data:
            inner_data['user_id'] = user_id
            inner_data['score'] = data[0]
            inner_data['credit_grade'] = str(data[1])
            inner_data['suggest_credit_amount'] = float(data[2])
            inner_data['state'] = data[3]

            if data[4]:
                f = json.loads(data[4])
                features['reg_date'] = f['base']['reg_date']
                features['reg_capital'] = f['base']['reg_capital']
                features['legal_age'] = f['base']['legal_age']
                features['invest'] = f['base']['investment_en_count']
                features['trade'] = f.get('trade')

        if period_data:
            if period_data[0]:
                period_dict = json.loads(period_data[0])
                synthesis_purchase = period_dict.get('synthesis_purchase')

        if company_data:
            business_name = ['58汽配', '巴图鲁', '精米', '点红', '车优品', '中驰车福', '亿采']
            for name in business_name:
                if name in company_data[2]:
                    n = name
            company_table['companyId'] = user_id
            company_table['companyName'] = str(company_data[0])
            company_table['businessAddress'] = str(company_data[1])
            company_table['businessName'] = name
            company_table['legalPerson'] = str(company_data[3])
            company_table['legalPersonPhone'] = company_data[4]
            company_table['contactPhone'] = company_data[5]
            company_table['regCapital'] = company_data[6]
            company_table['registrationDate'] = str(company_data[7])[0:10]
        return company_table,inner_data, features, synthesis_purchase

    @staticmethod
    def _get_check_pass_table(date_begin, date_end,businessAppId):  # 审核通过用户信息简表
        sql = '''select distinct C.enterprise_id , C.credit,
            C.mod_time,L.business_name,L.enterprise_name,L.enterprise_phone
            from credit C left join loan L
            on C.enterprise_id = L.enterprise_id
            where L.business_app_id = '%s'

            and C.mod_time between '%s' and '%s'
            '''  % (businessAppId, date_begin, date_end)
        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(sql)
        result = cursor_trade.fetchall()
        cursor_trade.close()
        conn_trade.close()
        check_pass_table = list()


        if result and len(result) > 0:
            for row in result:
                tr = dict()
                tr['enterprise_id'] = row[0]
                tr['credit'] = int(row[1])
                tr['mod_time'] = str(row[2])
                tr['business_name'] = row[3]
                tr['enterprise_name'] = row[4]
                tr['enterprise_phone'] = int(row[5])
                check_pass_table.append(tr)

        return check_pass_table


    @staticmethod
    def _get_check_reject_table(date_begin, date_end, businessAppId):  # 审核通过用户信息简表
        sql = '''select distinct R.enterpriseId , R.highestAmount,
               R.addTime,E.businessName,E.companyName,E.contactPhone
               from rc_info R left join enterprise E
               on R.enterpriseId = E.enterpriseId
               where E.businessAppId = '%s'

               and R.addTime between '%s' and '%s'
               ''' % (businessAppId, date_begin, date_end)
        conn_rc = db_rc.get_conn_rc()
        cursor_rc = conn_rc.cursor()
        cursor_rc.execute(sql)
        result = cursor_rc.fetchall()
        cursor_rc.close()
        conn_rc.close()
        logger.info('result_sql : %s',result)
        check_pass_table = list()

        if result and len(result) > 0:
            for row in result:
                tr = dict()
                tr['enterprise_id'] = row[0]
                tr['credit'] = int(row[1])
                tr['mod_time'] = str(row[2])
                tr['business_name'] = row[3]
                tr['enterprise_name'] = row[4]
                tr['enterprise_phone'] = int(row[5])
                check_pass_table.append(tr)
        logger.info('check_pass_table : %s',check_pass_table)
        return check_pass_table


    @staticmethod
    def _get_pass_total(date_begin, date_end,businessAppId):  # 通过
        check_sql = '''select count(id) from credit_task
                    where enterpriseId in(select enterpriseId from enterprise where version != 1 and businessAppId = '%s')
                    and version !=1 AND addTime between  '%s' AND  '%s'
                    and state IN (8,14,15,33) '''%  (businessAppId, date_begin, date_end)

        model_sql = '''SELECT count(id),sum(highestAmount)
                      from rc_info
                      where enterpriseId in (select enterpriseId from enterprise where version != 1 and businessAppId = '%s')
                      and version != 1 and rcLevel != 'CR6'
                      and addTime between '%s'and '%s'
                      ''' % (businessAppId, date_begin, date_end)
        reg_sql = '''select count(id),sum(credit) from credit
                    where enterprise_id in (select enterprise_id from loan where business_app_id = '%s')

                    and  add_time between '%s'and '%s'
                    ''' % (businessAppId, date_begin, date_end)
        conn_rc = db_rc.get_conn_rc()
        cursor_rc = conn_rc.cursor()

        cursor_rc.execute(check_sql)
        check_result = cursor_rc.fetchone()

        cursor_rc.execute(model_sql)
        model_result = cursor_rc.fetchone()
        cursor_rc.close()
        conn_rc.close()

        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(reg_sql)
        reg_result = cursor_trade.fetchall()
        cursor_trade.close()
        conn_trade.close()

        pass_total = list()
        pass_total.append(check_result[0])
        pass_total.append(model_result[1])

        for row in reg_result:
            pass_total.append(row[0])
            pass_total.append(row[1])

        return pass_total

    @staticmethod
    def get_credit_month(date_begin, date_end,businessAppId):
        # 按月统计授信情况
        # 模型跑出额度,推送额度,机构给出额度
        # 所有用户,审核通过,审核拒绝,模型通过,模型拒绝,机构通过,机构拒绝
        model_sql = '''SELECT DATE_FORMAT(addTime,"%%Y-%%m") as T,
        sum(CASE WHEN rcLevel !='CR6' AND version !=1 THEN highestAmount ELSE null END ),
        sum(CASE WHEN rcLevel !='CR6' AND version !=1 THEN reviseHighestAmount ELSE null END ),
        COUNT(DISTINCT(CASE WHEN rcLevel !='CR6' AND version !=1 THEN enterpriseId ELSE null END)) AS modelPass,
        COUNT(DISTINCT(CASE WHEN rcLevel ='CR6' AND version !=1 THEN enterpriseId ELSE null END)) AS modelReject
        from rc_info where enterpriseId in (select enterpriseId from enterprise where version != 1 and businessAppId = '%s')
        and version != 1
        and addTime between '%s'and '%s'
        group by T order by T
        ''' % (businessAppId,date_begin, date_end )

        reg_sql = '''SELECT DATE_FORMAT(add_time,'%%Y-%%m') M,
                SUM(credit ),
                count(  id  ),
                count(  id  )
                FROM credit  where enterprise_id in (select enterprise_id from loan where business_app_id = '%s')
                and add_time between '%s'and '%s'
                GROUP BY M  order by M
                ''' % (businessAppId,date_begin, date_end)

        conn_rc = db_rc.get_conn_rc()
        cursor_rc = conn_rc.cursor()
        cursor_rc.execute(model_sql)
        model_result = cursor_rc.fetchall()
        cursor_rc.close()
        conn_rc.close()

        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(reg_sql)
        reg_result = cursor_trade.fetchall()
        cursor_trade.close()
        conn_trade.close()

        model_months = list()
        push_months = list()
        reg_months = list()
        model_amount = list()
        push_amount = list()
        reg_amount = list()
        model_pass = list()
        model_reject = list()
        push_pass = list()
        reg_pass = list()
        reg_reject = list()

        for row in model_result:
            model_months.append(str(row[0] ))
            model_amount.append(int(row[1] // 10000))
            model_pass.append(int(row[3]))
            model_reject.append(row[4])
            push_months.append(str(row[0]))
            push_amount.append(int(row[2] // 10000))

        for row in reg_result:
            reg_months.append(row[0])
            reg_amount.append(int(row[1] // 10000))
            reg_pass.append(row[2])
            reg_reject.append(row[3])
        month_data = {
            'model_months':model_months,
            'push_months':push_months,
            'reg_months':reg_months,
            'model_amount':model_amount,
            'push_amount':push_amount,
            'reg_amount':reg_amount,
            'model_pass':model_pass,
            'model_reject':model_reject,
            'push_pass':push_pass,
            'reg_pass':reg_pass,
            'reg_reject':reg_reject
        }

        return json.dumps(month_data,ensure_ascii= False)

    @staticmethod
    def _get_credit_distribution1(date_begin, date_end,businessAppId):
        model_sql = '''SELECT highestAmount,reviseHighestAmount
               from rc_info
               where enterpriseId in (select enterpriseId from enterprise where version != 1 and businessAppId = '%s')
               and version != 1
               and addTime between '%s'and '%s'
               ''' % (businessAppId,date_begin, date_end)

        reg_sql = '''SELECT credit
                       FROM credit where enterprise_id in (select enterprise_id from loan where business_app_id = '%s')
                       and  add_time between '%s'and '%s'

                        ''' %  (businessAppId,date_begin, date_end)

        conn_rc = db_rc.get_conn_rc()
        cursor_rc = conn_rc.cursor()
        cursor_rc.execute(model_sql)
        model_result = cursor_rc.fetchall()
        cursor_rc.close()
        conn_rc.close()

        conn_trade = db_trade.get_conn_trade()
        cursor_trade = conn_trade.cursor()
        cursor_trade.execute(reg_sql)
        reg_result = cursor_trade.fetchall()
        cursor_trade.close()
        conn_trade.close()


        model_count = list()
        revise_count = list()
        reg_count = list()
        limit = [range(0, 1), range(1, 2), range(2, 3), range(3, 4), range(4, 5), range(5, 6), range(6, 7),
                 range(7, 8), range(8, 10)]
        for column in limit:

            model = 0
            revise = 0
            reg = 0
            for row in model_result:
                if int(row[0]) // 10000 in column:
                    model += 1
                if int(row[1]) // 10000 in column:
                    revise += 1
            for row in reg_result:
                if int (row[0]) // 10000 in column:
                    reg += 1
            model_count.append(model)
            revise_count.append(revise)
            reg_count.append(reg)

        model = 0
        revise = 0
        reg = 0
        for row in model_result:
            if int(row[0]) // 10000 > 10:
                model += 1
            if int(row[1]) // 10000 > 10:
                revise += 1
        for row in reg_result:
            if int(row[0]) // 10000 > 10:
                reg += 1

        model_count.append(model)
        revise_count.append(revise)
        reg_count.append(reg)

        dis = {
            "model_amount": model_count,
            "revise_amount": revise_count,
            "reg_amount": reg_count
        }

        return dis







