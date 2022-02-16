#!/usr/bin/env python
# encoding: utf-8

"""
@author: pyd
@file: testExport.py
@time: 2020/03/12
@desc:
"""
from tornado.web import RequestHandler
import pandas as pd

from utils.myLogger import infoLog
from sqlalchemy import create_engine


class ExportHandler(RequestHandler):

    def get(self):
        """
        （get方法，不是post）
        在run.py里apiTuples = [
            添加 (r"/xxx/xxx", ExportHandler)
        ]
        然后网页url访问xxx/xxx路径即可下载
        :return:
        """

        # req = self.request.body.decode('utf-8')
        # infoLog.info('/labor/export 接口产生调用')
        # infoLog.info('req: %s', str(req))

        # 从数据库查数据
        engine = create_engine('mysql+pymysql://root:root123@localhost:3306/test?charset=utf8')
        df = pd.read_sql_query('select ds from test_temperature limit 100;', engine)

        # 暂存路径
        file_path = 'C:/Users/97125/Desktop/temp.xlsx'
        # 下载的文件名
        file_name = 'output.xlsx'
        # 生成xlsx 有更多参数可以设置
        df.to_excel(file_path, sheet_name='Sheet1')
        # 设置导出的response
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        # ls = []
        # d1 = {'name': 'apple', 'color': 'red'}
        # d2 = {'name': 'banana', 'color': 'yellow'}
        # d3 = {'name': 'tomato', 'color': 'red'}
        # ls.append(d1)
        # ls.append(d2)
        # ls.append(d3)
        # df2 = pd.DataFrame(ls)
        # print(df2)

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.write(data)
        self.finish()
