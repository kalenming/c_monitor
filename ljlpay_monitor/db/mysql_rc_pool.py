# -*- coding: utf-8 -*-

import pymysql
from DBUtils.PooledDB import PooledDB

import logging
from config.config import *
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DbManagerRC(object):
    def __init__(self):
        kwargs_rc = {'host': HOST, 'user': USER_NAME_RC, 'passwd': PASSWORD_RC, 'db': DB_NAME_RC, 'charset': "utf8"}

        self._pool_rc = PooledDB(pymysql, mincached=3, maxcached=10, maxshared=10, maxusage=10000, **kwargs_rc)

    def get_conn_rc(self):
        return self._pool_rc.connection()

class DbManagerTRADE(object):
    def __init__(self):
        kwargs_trade = {'host': HOST, 'user': USER_NAME, 'passwd': PASSWORD, 'db': DB_NAME_TRADE, 'charset': "utf8"}
        self._pool_trade = PooledDB(pymysql, mincached=3, maxcached=10, maxshared=10, maxusage=10000, **kwargs_trade)


    def get_conn_trade(self):
        return self._pool_trade.connection()

    def query_one(self, sql):
        conn = self.get_conn_trade()
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            logger.exception(e)
        finally:
            cursor.close()
            conn.close()
        result = cursor.fetchone()
        return result

    def query_all(self, sql):
        conn = self.get_conn_trade()
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            logger.exception(e)
        finally:
            cursor.close()
            conn.close()
        result = cursor.fetchall()
        return result


db_rc = DbManagerRC()
db_trade = DbManagerTRADE()

