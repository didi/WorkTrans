#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql

db = pymysql.Connection(host='10.86.60.67', database='woqu', user='root', password='Ybaobao1', charset='utf8')


class DBInstence():

    def getDB(self):
        return db
