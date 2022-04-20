#!/usr/bin/env python
# encoding: utf-8

"""
@author: lidan
@contact: lidan@didiglobal.com
@file: getPos.py
@time: 2019-12-11 14:36
@desc:
"""

import json
from utils.testDBPool import DBPOOL
from utils.myLogger import infoLog, tracebackLog
from utils.global_keys import *
from utils.mysql_factory import Push_task_status_Query


class GetPosNum(RequestHandler):
    @gen.coroutine
    def post(self):
        try:
            raw_data = self.request.body.decode('utf-8')
            infoLog.info('GetPos : %s' % (raw_data.replace('\n', '')))
            raw_data = json.loads(raw_data)
            batch_id = raw_data.get("batch_id", None)
            result = {"code": 100, "result": "查询成功", "received_count": 0, "status": 0}
            if batch_id:
                res = yield self.Get_POS_Num(batch_id)
                result.update(res)
            else:
                result.update(RES_400)
            self.write(json.dumps(result))
        except Exception as e:
            tracebackLog.error('server error input={}'.format(self.request.body))
            tracebackLog.exception(e)
            self.write(json.dumps(RES_400))

    @staticmethod
    def check_param(raw_data):
        """
        验证参数合法性
        :param raw_data:
        :return: （code, result）code 0 为合法 其余为不合法
        """
        cid = raw_data.get('cid', None)
        did = raw_data.get('cid', None)
        batch_id = raw_data.get('batch_id', None)
        if not cid or not did or not batch_id:
            return False
        return True

    @gen.coroutine
    def Get_POS_Num(self, batch_id):
        try:
            conn = DBPOOL.connection()
            cursor = conn.cursor()
            sql = Push_task_status_Query.get_received_count()
            sql = sql % batch_id
            cursor.execute(sql)
            data = cursor.fetchone()
            cursor.close()
            conn.close()
            if len(data) == 2:
                return {"received_count": data[0], "status": data[1]}
        except Exception as e:
            tracebackLog.exception(e)
        return RES_400
