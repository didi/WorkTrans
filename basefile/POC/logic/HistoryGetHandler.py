"""
@author: shenzh
@contact: shenzihan_i@didichuxing.com
@file: calModify.py
@time: 2019-10-11 10:48
@desc:
"""
from utils.myLogger import infoLog
import datetime, time
from typing import Tuple, Dict, Any, List
import json
from utils.check_token import check_token
from POC.service.calService import CalService
from utils.testDBPool import DBPOOL
from utils.HistoryShiftUtils import HistoryShiftUtils

class HistoryGetHandller(RequestHandler):

    @gen.coroutine
    def initialize(self):
        self.cacheHistoryData = {}
        self.shiftUtils = HistoryShiftUtils

    def post(self):
        starttime = datetime.datetime.now()

        decodedata = self.request.body.decode('utf-8')
        infoLog.info('HistoryGetHandller : {}'.format (decodedata))

        code, notice, queryDict = self.check_param(decodedata)

        result = {}
        try:
          result = yield self.shiftUtils.getHistory(queryDict)
        except Exception as e:
            print(e)
        self.write(result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'HistoryGetHandller'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str,dict]:
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误',None

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误',None

        return 0, '',raw_data








