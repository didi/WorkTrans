#!/usr/bin/env python
# encoding: utf-8

"""
@author: lidan
@contact: lynnlidan@didiglobal.com
@file: lforecastModifyCls.py
@time: 2019-08-26 20:15
@desc:
"""
import json
from typing import Dict, Tuple
import datetime
import time
from utils.check_token import check_token
from labor.service.labor_db_service import LaborDbService
from utils.myLogger import infoLog, tracebackLog

class LForecastModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('LForecastModifyHandler : %s' % (self.request.body.decode('utf-8').replace('\n','')))
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
            self.write(save_result)

        else:
            code = yield LaborDbService.labor_cacl_value_modify(raw_data)
            if code == 100:
                self.write({'code': 100, 'result': '处理成功'})
            else:
                self.write({'code': 400, 'result': '其他错误'})
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'LForecastModifyHandler'
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

        if 'timestr' not in raw_data or 'token' not in raw_data:
            return 3, '未包含token'

        if not ('cid' in raw_data and 'forecastModifyArr' in raw_data ):
            return 3, 'post json参数错误：cid,forecastModifyArr,forecastModifyArr[forecastDate、startTimeStr、forecastValue、editValue]为必传参数'

        for m in raw_data['forecastModifyArr']:
            if 'forecastDate' in m and 'startTimeStr' in m and 'forecastValue' in m and 'editValue' in m and 'endTimeStr' in m :
                        if not ('taskBid' in m and 'laborStandardBid' in m ): # and 'forecastStandard' in m
                           return 4, 'forecastModifyArr[taskBid、laborStandardBid] 为必传参数' #、forecastStandard
            else:
                return 5, 'forecastModifyArr[forecastDate、startTimeStr、endTimeStr、forecastValue、editValue] 为必传参数'


        return 0, ''