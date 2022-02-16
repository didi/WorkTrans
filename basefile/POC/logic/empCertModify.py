"""
@author: shenzh
@contact: shenzihan_i@didichuxing.com
@file: empCertModify.py
@time: 2019-10-09 14:48
@desc:
"""
from tornado.web import RequestHandler
import json,datetime,time
from typing import Dict, Tuple
from utils.check_token import check_token
from utils.myLogger import infoLog
from POC.service.empCertService import empCertService
from tornado import gen

class  EmpCertModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('EmpCertModifyHandler : %s' % (self.request.body.decode('utf-8').replace('\n','')))
        s = datetime.datetime.now()

        # 参数检验
        code, notice = self.check_param(self.request.body.decode('utf-8'))
        if code:
            save_result = {'code': 400 + code, 'result': notice}
            self.write(save_result)
            return

        raw_data: Dict = json.loads(self.request.body.decode('utf-8'))

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        # token检验
        code, result = check_token(token, time_str)
        if code:
            save_result = {'code': code, 'result': result}
            self.write(save_result)
        else:
            save_result = yield empCertService.doRequest(raw_data)
            self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'EmpCertModifyHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

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

        if 'cid' not in raw_data or 'skillData' not in raw_data:
            return 2, '参数错误,需要包含cid，skillData'

        if not isinstance(raw_data['skillData'], list):
            return 2, '参数错误,skillData需要为list'

        for entity in raw_data['skillData']:
            if 'eid' not in entity or 'opt' not in entity or 'certs' not in entity:
                return 2, '参数错误,skillData的每条数据需要包含eid,opt,certs'

            if entity['opt'] not in ['update']:
                return 2, '参数错误,opt只能为update'

            if not isinstance(entity['certs'],list):
                return 2, '参数错误,certs需要为list'

            if entity['opt'] == 'update':
                for entity1 in entity['certs']:
                    if 'certname' not in entity1 or 'closingdate' not in entity1:
                        return 2,'参数错误,certs的每条数据需要包含certname,closingdate'
        return 0, ''