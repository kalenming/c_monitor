# -*-encoding:utf-8 -*-
import json
from datetime import date,datetime, timedelta
from ljlpay_monitor.db.mysql_rc_pool import db_rc
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
pdfmetrics.registerFont(TTFont('simsun', './pdf/simsun.ttf'))
from reportlab.lib import fonts,colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,Image,Table,TableStyle
fonts.addMapping('./report/simsun', 0, 0, 'simsun')



class Report(object):
    def __init__(self):
        pass

    def daily_report(self):

        today = datetime.today()
        day_begin = datetime(today.year, today.month, today.day, 0, 0, 0)
        day_begin = str(day_begin)[0:19]
        day = str(day_begin)[0:10]
        time_begin = datetime.strptime(day_begin, '%Y-%m-%d %H:%M:%S')

        collect = self.report_collect(time_begin)
        checked_table, overdue_table, checked_table_pdf, overdue_table_pdf = self.report_detail_table(time_begin)
        logger.info('daily_collect:%s', collect)

        #写入pdf
        doc = SimpleDocTemplate("./pdf/daily_report.pdf", pagesize=letter)
        story = []
        stylesheet = getSampleStyleSheet()
        normalStyle = stylesheet['Normal']
        rpt_title = '<para autoLeading="off" fontSize=15 align=center><b><font face="simsun">项目日报%s</font></b><br/><br/><br/></para>'%(day)
        story.append(Paragraph(rpt_title, normalStyle))

        text = '<para autoLeading="off" fontSize=9><br/><br/><br/><b><font face="simsun">今日进件信息：</font></b><br/></para>'
        story.append(Paragraph(text, normalStyle))
        table_data_pdf = list()
        table_data_pdf.insert(0, ['今日新进数量', '今日审核数量', '今日审核通过', '今日审核拒绝', '今日逾期数量'])
        table_data_pdf.append([collect['new'], collect['checked'],collect['checkedPass'],
                               collect['checkedReject'], collect['overdue']])
        component_table = Table(table_data_pdf, colWidths=[100, 100, 100, 100, 100])
        component_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 字体
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
            ('BACKGROUND', (0, 0), (6, 0), colors.lightskyblue),  # 设置第一行背景颜色
            ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
            ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.red),  # 设置表格框线为红色，线宽为0.5
        ]))
        story.append(component_table)

        checked_data_pdf = list()
        company_count = 0
        text = '<para autoLeading="off" fontSize=9><br/><br/><br/><b><font face="simsun">今日授信信息表：</font></b><br/></para>'
        checked_data_pdf.append(['企业名称', '模型等级', '推送等级', '模型额度', '推送额度', '状态标识', '时间'])
        for row in checked_table_pdf:
             checked_data_pdf.append(row)

        component_table = Table(checked_data_pdf, colWidths=[200, 50, 50, 50, 50,50,110])
        component_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 字体
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
            ('BACKGROUND', (0, 0), (8, 0), colors.lightskyblue),  # 设置第一行背景颜色
            ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
            ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.red),  # 设置表格框线为红色，线宽为0.5
        ]))
        story.append(Paragraph(text, normalStyle))
        story.append(component_table)


        text = '<para autoLeading="off" fontSize=9><br/><br/><br/><b><font face="simsun">今日逾期信息表：</font></b><br/></para>'
        story.append(Paragraph(text, normalStyle))
        overdue_data_pdf = list()
        company_count = 0
        overdue_data_pdf.append(['企业名称', '逾期金额', '电商平台', '模型额度', '推送额度', '机构额度', '时间'])
        for row in overdue_table_pdf:
            overdue_data_pdf.append(row)

        component_table = Table(overdue_data_pdf, colWidths=[150, 50, 150, 50, 50, 50, 110])
        component_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 字体
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
            ('BACKGROUND', (0, 0), (8, 0), colors.lightskyblue),  # 设置第一行背景颜色
            ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
            ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.red),  # 设置表格框线为红色，线宽为0.5
        ]))
        story.append(component_table)



        for tr in checked_table :
            company_table_pdf = list()
            companyName = tr['companyName']
            print companyName
            text = '<para autoLeading="off" fontSize=9><br/><br/><br/><b><font face="simsun">%s</font></b><br/></para>' % (companyName)
            story.append(Paragraph(text, normalStyle))
            company_table_pdf.append(['时段', '量(件)', '金额(元)', '次数', '品类(种)', '退货率(%)'])
            if tr['trade_flow']:
                keys = ['month', 'two_months', 'quarter_year', 'half_year', 'one_year']
                for key in keys:
                    period_flow = tr['trade_flow'].get(key, 0)
                    if period_flow:
                        data = [key,period_flow['goods_quantity'],period_flow['amount'],period_flow['order_count'],period_flow['goods_type'],period_flow['refund_rate']]
                        company_table_pdf.append(data)
            component_table = Table(company_table_pdf, colWidths=[100, 100, 100, 100, 100, 100])
            component_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 字体
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
                ('BACKGROUND', (0, 0), (8, 0), colors.lightskyblue),  # 设置第一行背景颜色
                ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
                ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),  # 设置表格内文字颜色
                ('GRID', (0, 0), (-1, -1), 0.5, colors.red),  # 设置表格框线为红色，线宽为0.5
            ]))
            story.append(component_table)


        doc.build(story)


        daily = {
            'collect': collect,
            'checked_table': checked_table,
            'overdue_table': overdue_table
        }
        return daily

    def week_report(self):
        today = datetime.today()
        weekdays = today.weekday()
        week_begin = today - timedelta(days=weekdays)
        week_begin = datetime(week_begin.year, week_begin.month, week_begin.day, 0, 0, 0)
        week_begin = str(week_begin)[0:19]
        time_begin = datetime.strptime(week_begin, '%Y-%m-%d %H:%M:%S')
        collect = self.report_collect(time_begin)
        checked_table, overdue_table, checked_table_pdf, overdue_table_pdf = self.report_detail_table(time_begin)
        logger.info('daily_collect:%s', collect)

        # 写入pdf
        doc = SimpleDocTemplate("./pdf/weekly_report.pdf", pagesize=letter)
        story = []
        stylesheet = getSampleStyleSheet()
        normalStyle = stylesheet['Normal']
        rpt_title = '<para autoLeading="off" fontSize=15 align=center><b><font face="simsun">项目周报</font></b><br/><br/><br/></para>'
        story.append(Paragraph(rpt_title, normalStyle))

        text = '<para autoLeading="off" fontSize=9><br/><br/><br/><b><font face="simsun">本周进件信息：</font></b><br/></para>'
        story.append(Paragraph(text, normalStyle))
        table_data_pdf = list()
        table_data_pdf.insert(0, ['本周新进数量', '本周审核数量', '本周审核通过', '本周审核拒绝', '本周逾期数量'])
        table_data_pdf.append([collect['new'], collect['checked'], collect['checkedPass'],
                               collect['checkedReject'], collect['overdue']])
        component_table = Table(table_data_pdf, colWidths=[100, 100, 100, 100, 100])
        component_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 字体
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
            ('BACKGROUND', (0, 0), (6, 0), colors.lightskyblue),  # 设置第一行背景颜色
            ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
            ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.red),  # 设置表格框线为红色，线宽为0.5
        ]))
        story.append(component_table)

        checked_data_pdf = list()
        company_count = 0
        text = '<para autoLeading="off" fontSize=9><br/><br/><br/><b><font face="simsun">本周授信信息表：</font></b><br/></para>'
        checked_data_pdf.append(['企业名称', '模型等级', '推送等级', '模型额度', '推送额度', '状态标识', '时间'])
        for row in checked_table_pdf:
            checked_data_pdf.append(row)

        component_table = Table(checked_data_pdf, colWidths=[200, 50, 50, 50, 50, 50, 110])
        component_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 字体
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
            ('BACKGROUND', (0, 0), (8, 0), colors.lightskyblue),  # 设置第一行背景颜色
            ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
            ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.red),  # 设置表格框线为红色，线宽为0.5
        ]))
        story.append(Paragraph(text, normalStyle))
        story.append(component_table)

        text = '<para autoLeading="off" fontSize=9><br/><br/><br/><b><font face="simsun">本周逾期信息表：</font></b><br/></para>'
        story.append(Paragraph(text, normalStyle))
        overdue_data_pdf = list()
        company_count = 0
        overdue_data_pdf.append(['企业名称', '逾期金额', '电商平台', '模型额度', '推送额度', '机构额度', '时间'])
        for row in overdue_table_pdf:
            overdue_data_pdf.append(row)

        component_table = Table(overdue_data_pdf, colWidths=[150, 50, 150, 50, 50, 50, 110])
        component_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 字体
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
            ('BACKGROUND', (0, 0), (8, 0), colors.lightskyblue),  # 设置第一行背景颜色
            ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
            ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.red),  # 设置表格框线为红色，线宽为0.5
        ]))
        story.append(component_table)

        for tr in checked_table:
            company_table_pdf = list()
            companyName = tr['companyName']
            print companyName
            text = '<para autoLeading="off" fontSize=9><br/><br/><br/><b><font face="simsun">%s</font></b><br/></para>' % (
            companyName)
            story.append(Paragraph(text, normalStyle))
            company_table_pdf.append(['时段', '量(件)', '金额(元)', '次数', '品类(种)', '退货率(%)'])
            if tr['trade_flow']:
                keys = ['month', 'two_months', 'quarter_year', 'half_year', 'one_year']
                for key in keys:
                    period_flow = tr['trade_flow'].get(key, 0)
                    if period_flow:
                        data = [key, period_flow['goods_quantity'], period_flow['amount'], period_flow['order_count'],
                                period_flow['goods_type'], period_flow['refund_rate']]
                        company_table_pdf.append(data)
            component_table = Table(company_table_pdf, colWidths=[100, 100, 100, 100, 100, 100])
            component_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 字体
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # 字体大小
                ('BACKGROUND', (0, 0), (8, 0), colors.lightskyblue),  # 设置第一行背景颜色
                ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
                ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),  # 设置表格内文字颜色
                ('GRID', (0, 0), (-1, -1), 0.5, colors.red),  # 设置表格框线为红色，线宽为0.5
            ]))
            story.append(component_table)

        doc.build(story)

        daily = {
            'collect': collect,
            'checked_table': checked_table,
            'overdue_table': overdue_table
        }
        return daily


    @staticmethod
    def report_collect(time_begin ):
        # 新进用户查询语句
        sql_new = """
        SELECT COUNT(DISTINCT(enterpriseId)) AS allCount
        FROM credit_task
        WHERE version !=1
        AND addTime > '%s'  """ % (time_begin)

        sql_check = """
            SELECT
            COUNT(DISTINCT(CASE WHEN state !=0 THEN enterpriseId ELSE null END)) AS checked,
            COUNT(DISTINCT(CASE WHEN state IN (8,14,15,33) THEN enterpriseId ELSE null END)) AS checkPass,
            COUNT(DISTINCT(CASE WHEN state IN (1,11,12) THEN enterpriseId ELSE null END)) AS checkReject
            FROM credit_task
            WHERE version !=1
            AND addTime > '%s'
        """ % (time_begin)

        # 逾期用户查询语句
        sql_overdue = """
            SELECT COUNT(DISTINCT(enterprise_id))
            FROM loan WHERE version !=1
            AND overdue_time > '%s'
        """ % (time_begin)

        conn = db_rc.get_conn()
        cursor = conn.cursor()
        # 执行当日新进用户查询
        cursor.execute(sql_new)
        result_new = cursor.fetchone()
        # 执行当日审核用户查询
        cursor.execute(sql_check)
        result_check = cursor.fetchone()
        # 执行当日逾期用户查询
        cursor.execute(sql_overdue)
        result_overdue = cursor.fetchone()
        cursor.close()
        conn.close()


        collect = {
            'new': result_new[0],  # 当日新进数量
            'checked': result_check[0],  # 当日审核数量
            'checkedPass': result_check[1],  # 当日审核通过数量
            'checkedReject': result_check[2],  # 当日审核拒绝数量
            'overdue': result_overdue[0]  # 当日逾期数量
        }

        return collect

    @staticmethod
    def report_detail_table(time_begin):
        # 当日审核的用户授信信息查询语句
        sql_checked = """
            SELECT distinct E.companyName,R.rcLevel,R.reviseRcLevel,
            COALESCE(highestAmount, 0),COALESCE(R.reviseHighestAmount, 0),
            C.state, C.addTime,
            Z.period_static
            FROM credit_task C LEFT JOIN rc_info R ON C.enterpriseId = R.enterpriseId
            LEFT JOIN enterprise E ON C.enterpriseId = E.enterpriseId
            LEFT JOIN zc_history_static Z ON E.enterpriseId = Z.enterprise_id
            WHERE C.state IN (8,12,14,15,33)
            AND C.version !=1 AND E.version !=1 AND Z.version !=1 AND R.version !=1
            AND C.addTime > '%s'
            ORDER BY C.state
        """ % (time_begin)
        # 当日发生逾期的用户逾期金额查询语句
        sql_overdue_loan = """
            SELECT MAX(DISTINCT(enterprise_id)) ID ,SUM(loan_amount)
            FROM loan
            WHERE version !=1 AND overdue_time > '%s'  and state = 8
            GROUP BY enterprise_id ORDER BY ID
        """ % (time_begin)
        # 当日发生逾期的用户其他信息查询语句
        sql_overdue_info = """
            SELECT E.companyName, E.businessName,R.rcLevel,R.reviseRcLevel,
            R.highestAmount,R.reviseHighestAmount, EC.credit,EC.addTime
            FROM enterprise E
            LEFT JOIN rc_info R ON E.id = R.enterpriseId
            LEFT JOIN enterprise_credit EC ON E.id = EC.enterpriseId
            WHERE E.version !=1 AND R.version !=1 AND EC.version !=1
            AND E.enterpriseId IN (SELECT DISTINCT enterprise_id FROM loan
            WHERE state = 8 AND version!=1 AND overdue_time > '%s'  )
            ORDER BY E.id
        """ % (time_begin)

        conn = db_rc.get_conn()
        cursor = conn.cursor()
        cursor.execute(sql_checked)
        # 当日审核用户信息查询结果
        checked_result = cursor.fetchall()
        cursor.execute(sql_overdue_loan)
        # 当日逾期用户金额查询结果
        overdue_loan = cursor.fetchall()
        cursor.execute(sql_overdue_info)
        # 当日逾期用户其他信息查询结果
        overdue_info = cursor.fetchall()
        cursor.close()
        conn.close()
        checked_table = list()
        checked_table_pdf = list()
        # 从SQL记录中取出审核结果
        for row in checked_result:
            tr = dict()
            tr['companyName'] = row[0]   # 企业名称
            logger.info('checked_table-companyName:%s', tr['companyName'])
            tr['rcLevel'] = row[1]  # 模型等级
            logger.info('checked_table-rcLevel:%s', tr['rcLevel'])
            tr['reviseRcLevel'] = row[2]  # 推送等级
            logger.info('checked_table-reviseRcLevel:%s', tr['reviseRcLevel'])
            tr['highestAmount'] = int(row[3])   # 模型额度
            logger.info('checked_table-highestAmount:%s', tr['highestAmount'])
            tr['reviseHighestAmount'] = int(row[4])  # 推送额度
            logger.info('checked_table-reviseHighestAmount:%s', tr['reviseHighestAmount'])
            tr['state'] = row[5]  # 状态
            logger.info('checked_table-state:%s', tr['state'])
            tr['time'] = row[6]  # 时间
            logger.info('checked_table-time:%s', tr['time'])
            checked_table_pdf.append([row[0],row[1],row[2],int(row[3]),int(row[4]),row[5],row[6]])

            if row[7]:
                # 交易流水
                period_dict = json.loads(row[7])
                tr['trade_flow'] = period_dict.get('synthesis_purchase')
                logger.info('trade_flow:%s', tr['trade_flow'])
            else:
                tr['trade_flow'] = {}
            checked_table.append(tr)
        overdue_table = list()
        list_index = 0

        overdue_table_pdf = list()
        # 将逾期金额和逾期其他信息拼接起来组成一个表
        for row in overdue_info:
            tr = dict()
            tr['ID'] = overdue_loan[list_index][0]
            logger.info('overdue_table-ID:%s', tr['ID'])
            tr['loan_amount'] = overdue_loan[list_index][1]
            logger.info('overdue_table-loan_amount:%s', tr['loan_amount'])
            tr['companyName'] = row[0]
            logger.info('overdue_table-companyNameD:%s', tr['companyName'])
            tr['businessName'] = row[1]
            logger.info('overdue_table-businessName:%s', tr['businessName'])
            tr['rcLevel'] = row[2]
            logger.info('overdue_table-rcLevel:%s', tr['rcLevel'])
            tr['reviseRcLevel'] = row[3]
            logger.info('overdue_table-reviseRcLevel:%s', tr['reviseRcLevel'])
            tr['highestAmount'] = int(row[4])
            logger.info('overdue_table-highestAmount:%s', tr['highestAmount'])
            tr['reviseHighestAmount'] = int(row[5])
            logger.info('overdue_table-reviseHighestAmount:%s', tr['reviseHighestAmount'])
            tr['credit'] = int(row[6])
            logger.info('overdue_table-credit:%s', tr['credit'])
            tr['time'] = row[7]
            logger.info('overdue_table-time:%s', tr['time'])
            overdue_table.append(tr)
            list_index += 1
            overdue_table_pdf.append([row[0], overdue_loan[list_index][1], row[1], int(row[4]), int(row[5]),int(row[6]),row[7]])
        return checked_table, overdue_table,checked_table_pdf,overdue_table_pdf
