"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: AvailableTimeModify.py
@time: 2019-10-9 14:28
@desc:
"""
from tornado.web import RequestHandler
import json,datetime,time
from typing import Dict, Tuple
from utils.check_token import check_token
from utils.myLogger import infoLog
from POC.service.AvailableTimeService import AvailableTimeService
from tornado import gen

class AvailableTimeHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('AvailableTimeHandler : %s' % (self.request.body.decode('utf-8').replace('\n','')))
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
            try:
                save_result = yield AvailableTimeService.doRequest(raw_data)
                self.write(save_result)
            except Exception as e:
                infoLog.error(e)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'AvailableTimeHandler'
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

        if 'cid' not in raw_data or 'availabletime' not in raw_data:
            return 2, '参数错误,需要包含cid，availabletime'

        if not isinstance(raw_data.get("availabletime",""),list):
            return 2, "参数错误，availabletime必须是一个Array"

        for item in raw_data.get("availabletime",""):
            if "eid" not in item or "opt" not in item or "type" not in item or\
                    "day" not in item:
                return 2, "参数错误，availabletime必须包含eid、opt、type、day"

            if item.get("opt","") not in ['update','delete']:
                return 2, "参数错误，opt的值必须为update或delete"

            if item.get("type","") not in ["0","1","2"]:
                return 2, "参数错误，type的值必须为0、1、2"

            if "times" in item:
                if not isinstance(item.get("times", ""), list):
                    return 2, "参数错误，times必须是一个Array"

                for item2 in item.get("times"):
                    if "start" not in item2 or "end" not in item2:
                        return 2, "参数错误，times必须包含start、end"

        return 0, ''