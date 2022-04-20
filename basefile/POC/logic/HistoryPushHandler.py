"""
@author: shenzh
@contact: shenzihan_i@didichuxing.com
@file: calModify.py
@time: 2019-10-11 10:48
@desc:
"""
from utils.myLogger import infoLog
import datetime
from typing import Tuple, Dict, Any, List
import json, datetime, time
from utils.check_token import check_token
from POC.service.calService import CalService
from utils.testDBPool import DBPOOL
from utils.HistoryShiftUtils import HistoryShiftUtils

class HistoryPushHandler(RequestHandler):
    '''
    每给喔趣返回一个确定的排班结果，就需要在此修改一下
    '''

    def initialize(self):
        self.cacheHistoryData = {}
        self.shiftUtls= HistoryShiftUtils
        # TODO 从数据库中将所有历史排班信息缓存起来


    def HHMMSSDiff(self,h1,h2):
        t1 = datetime.datetime.strptime(h1, "%Y-%m-%d %H:%M:%S")
        t2 = datetime.datetime.strptime(h2, "%Y-%m-%d %H:%M:%S")
        dtl = t2 - t1
        return dtl.seconds / 60

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('HistoryPushHandler : %s' % (self.request.body.decode('utf-8')))
        s = datetime.datetime.now()
        param = self.request.body.decode('utf-8')

        code, notice,raw_data = self.check_param(param)

        try:
            yield self.shiftUtls.saveShiftResult(raw_data)
        except Exception as e:
           pass


        self.write("ok")
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'HistoryPushHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str,dict]:
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误',raw_data

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误',raw_data

        # if 'timestr' not in raw_data or 'token' not in raw_data:
        #     return 3, '未包含token',raw_data

        # if 'cid' not in raw_data or 'applyId' not in raw_data:
        #     return 2, '参数错误，需要包含cid, applyId',raw_data

        # if not isinstance(raw_data['editData'], list):
        #     return 2, '参数错误,editData需要为list',raw_data
        #
        # for entity in raw_data['editData']:
        #     if 'eid' not in entity or 'schDay' not in entity or 'allWorkTime' not in entity or 'workUnit' not in entity:
        #         return 2, '参数错误,editData的每条数据需要包含eid,schDay,allWorkTime,workUnit',raw_data
        #
        #     if not isinstance(entity['workUnit'],list):
        #         return 2, '参数错误,workUnit需要为list',raw_data
        #
        #     for entity1 in entity['workUnit']:
        #         if 'type' not in entity1 or 'outId' not in entity1 or 'startTime' not in entity1 or 'endTime' not in entity1 or 'workTime' not in entity1:
        #             return 2,'参数错误,workUnit的每条数据需要包含type,outId,startTime,endTime,workTime',raw_data
        for entity in raw_data['data']['cal']:
            if 'eid' not in entity \
                    or 'schDay' not in entity \
                    or 'allWorkTime' not in entity \
                    or 'workUnit' not in entity:
                return 2, '参数错误,cal的每条数据需要包含eid,schDay,allWorkTime,workUnit', None

            if not isinstance(entity['workUnit'], list):
                return 2, '参数错误,workUnit需要为list', None

            for entity1 in entity['workUnit']:
                # 下面的if 中先不假shiftId的判断：or 'shiftId' not in entity1
                if 'type' not in entity1 \
                        or 'outId' not in entity1 \
                        or 'startTime' not in entity1 \
                        or 'endTime' not in entity1 \
                        or 'workTime' not in entity1:
                    return 2, '参数错误,workUnit的每条数据需要包含type,outId,startTime,endTime,workTime', None

        return 0, '',raw_data



