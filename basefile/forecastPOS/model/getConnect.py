#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql

db = pymysql.Connection(host='mysql_ip', database='woqu', user='root', password='Ybaobao1', charset='utf8')


class DBInstence():

    def getDB(self):
        return db
