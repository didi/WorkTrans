#!/usr/bin/env python
# encoding: utf-8

"""
@author: lidan
@contact: lidan@didiglobal.com
@file: getData.py
@time: 2019-12-11 14:36
@desc:
"""
from tornado.web import RequestHandler
import json,datetime, time
from typing import Dict, Tuple
from utils.testDBPool import DBPOOL
from utils.myLogger import infoLog
from tornado import gen

class GetData(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        raw_data = self.request.body.decode('utf-8')
        infoLog.info('GetData : %s' % (raw_data.replace('\n', '')))

        print(raw_data)
        code, notice = self.check_param(raw_data)
        print(code, notice)
        data={}
        if code!=0:
            data={"notice":notice}
        else:
            data= yield self.getData(raw_data)
        result={"code":100,"data":[data]}
        print(data[0:5])
        self.write({"code":100,"data":data})
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'GetData'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str]:
        """
        验证参数合法性
        :param input_json_string:
        :return: （code, result）code 0 为合法 其余为不合法
        """
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误'

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误'
        else:
            tablename=raw_data.get('tablename', '')
            print(tablename)
            if tablename not in ['劳动力标准','班次模板','组合规则','拆分规则','员工技能','员工匹配规则','员工证书','劳动任务详情','员工可用性','排班合规性','测试']:
                return 3, 'tablename不合法，支持：劳动力标准、班次模板、组合规则、拆分规则、员工技能、员工匹配规则、员工证书、劳动任务详情、劳动任务详情、员工可用性、排班合规性、测试'
        return 0,'passed'



    @staticmethod
    @gen.coroutine
    def getData(raw_data):
        print('raw_data',raw_data)
        raw_data = json.loads(raw_data)
        #emp_skill,labor_taskemp_matchpro,employee_certificate,labor_comb_rule,labor_shift_split_rule,labor_standard,labor_task,sch_available_time,shift_mod_data
        tablename=raw_data.get('tablename','')
        if tablename=='员工技能':
            tablename='emp_skill'
        elif tablename=='员工匹配规则':
            tablename='emp_matchpro'
        elif tablename=='员工证书':
            tablename='employee_certificate'
        elif tablename == '组合规则':
            tablename = 'labor_comb_rule'
        elif tablename == '拆分规则':
            tablename = 'labor_shift_split_rule'
        elif tablename == '劳动力标准':
            tablename = 'labor_standard'
        elif tablename == '劳动任务详情':
            tablename = 'labor_task'
        elif tablename == '劳动任务详情':
            tablename = 'labor_task'
        elif tablename == '员工可用性':
            tablename = 'sch_available_time'
        elif tablename == '班次模板':
            tablename = 'shift_mod_data'
        elif tablename == '排班合规性':
            tablename = 'sch_compliance'
        elif tablename == '测试':
            tablename = 'test'

        else:
            tablename='employee'
        a={}
        if tablename=='test':
            a={'haha':'100'}
        else:
            a=GetData.getDataFromDB(tablename)
        print(a)
        raise gen.Return(a)




    @staticmethod
    def getDataFromDB(tablename):
        conn = DBPOOL.connection()
        res=[]
        with conn.cursor() as cursor:
            sql = """select * from %s where status=1 order by auto_id desc""" %tablename
            cursor.execute(sql)
            a=cursor.description
            m=[]
            for t in a:
                #if t[0].find('date')==-1 and t[0].find('time')==-1 and t[0].find('day')==-1 and t[0].find('shift_start')==-1 and t[0].find('shift_end')==-1 :
                    m.append(t[0])
            res.append('    '.join(m))
            rest=cursor.fetchall()
            for  i in rest:
                j=[]
                for t in i:
                    #if not (isinstance(t, datetime.datetime) or isinstance(t, datetime.timedelta) or isinstance(t, datetime.date)):
                        j.append(str(t))
                res.append('    '.join(j))
        conn.close()
        return res

if __name__ == '__main__':
    for k in ['排班合规性']:#['劳动力标准','班次模板','组合规则','拆分规则','员工技能','员工匹配规则','员工证书','劳动任务详情','员工可用性']:
        a={"tablename":k}
        print()
        print()
        print()
        print(a)
        rest=GetData.getData(a)
        for i in rest[0:3]:
            print(i)