#!/usr/bin/env python
# encoding: utf-8

"""
@author: lidan
@contact: lidan@didiglobal.com
@file: getPos.py
@time: 2019-12-11 14:36
@desc:
"""
import json,datetime, time
from typing import Dict, Tuple
from utils.testDBPool import DBPOOL
from utils.myLogger import infoLog

class GetPoscnt(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        raw_data = self.request.body.decode('utf-8')
        infoLog.info('GetPoscnt : %s' % (raw_data.replace('\n', '')))

        print(raw_data)
        code, notice = self.check_param(raw_data)
        print(code, notice)
        data={}
        if code!=0:
            data={"notice":notice}
        else:
            raw_data = json.loads(raw_data)
            cid=raw_data.get('cid','')
            did=raw_data.get('did','')
            data=yield self.getDataFromDB(cid,did)
        result={"code":100,"data":[data]}
        print(data[0:5])
        self.write({"code":100,"data":data})
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'GetPoscnt'
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
            cid=raw_data.get('cid', '')
            did=raw_data.get('cid', '')

            if cid=='' or did=='' :
                return 3, '请给出cid,did'
        return 0,'passed'



    @staticmethod
    @gen.coroutine
    def getDataFromDB(cid,did):
        conn = DBPOOL.connection()
        res=[]
        with conn.cursor() as cursor:
            sql = "select cid,did,substr(gmt_bill,1,10) as day,count(1) from base_pos_df where aistatus=1 and cid=%s and did=%s group by cid,did,substr(gmt_bill,1,10) order by cid,did,day;"
            cursor.execute(sql,(cid,did))
            a=cursor.description
            m=[]
            for t in a:
                #if t[0].find('date')==-1 and t[0].find('time')==-1 and t[0].find('day')==-1 and t[0].find('shift_start')==-1 and t[0].find('shift_end')==-1 :
                    m.append(t[0])
            res.append(', '.join(m))
            rest=cursor.fetchall()
            for  i in rest:
                j=[]
                for t in i:
                    #if not (isinstance(t, datetime.datetime) or isinstance(t, datetime.timedelta) or isinstance(t, datetime.date)):
                        j.append(str(t))
                res.append(', '.join(j))
        conn.close()
        raise gen.Return(res)

if __name__ == '__main__':
   a= GetPoscnt.getDataFromDB('51000447','14')
   for t in a:
       print(t)