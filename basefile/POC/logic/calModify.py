"""
@author: shenzh
@contact: shenzihan_i@didichuxing.com
@file: calModify.py
@time: 2019-10-11 10:48
@desc:
"""
from tornado.web import RequestHandler
from utils.myLogger import infoLog
import datetime, time
from typing import Tuple, Dict, Any, List
import json
from utils.check_token import check_token
from POC.service.calService import CalService
from tornado import gen

class CalModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = time.time()
        infoLog.info('CalModifyHandler : %s' % (self.request.body.decode('utf-8').replace('\n','')))
        s = datetime.datetime.now()
        code, notice = self.check_param(self.request.body.decode('utf-8'))

        if code:
            save_result = {'code': 400 + code, 'result': notice}
            self.write(save_result)
            return

        raw_data: Dict = json.loads(self.request.body.decode('utf-8'))

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        code, result = check_token(token, time_str)
        if code:
            save_result = {'code': code, 'result': result}
        else:
            save_result = yield CalService.doRequest(raw_data)
        self.write(save_result)
        endtime = time.time()
        infoLog.info('CalModifyHandler time_cost:{:.4f}s'.format(endtime-starttime))
    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str]:
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误'

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误'

        if 'timestr' not in raw_data or 'token' not in raw_data:
            return 3, '未包含token'

        if 'cid' not in raw_data:
            return 2, '参数错误，需要包含cid'

        if not isinstance(raw_data['editData'], list):
            return 2, '参数错误,editData需要为list'

        for entity in raw_data['editData']:
            if 'eid' not in entity or 'schDay' not in entity  or 'workUnit' not in entity:
                return 2, '参数错误,editData的每条数据需要包含eid,schDay,workUnit'

            if not isinstance(entity['workUnit'],list):
                return 2, '参数错误,workUnit需要为list'

            for entity1 in entity['workUnit']:
                if 'type' not in entity1 or 'outId' not in entity1 or 'startTime' not in entity1 or 'endTime' not in entity1 :
                    return 2,'参数错误,workUnit的每条数据需要包含type,outId,startTime,endTime'

        return 0, ''



