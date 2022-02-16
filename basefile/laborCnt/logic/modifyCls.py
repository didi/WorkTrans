#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: modifyCls.py
@time: 2019/9/10 11:59 上午
@desc:
"""
from tornado.web import RequestHandler
from typing import Tuple
import json
import datetime
import time
from utils.check_token import check_token
from utils.myLogger import infoLog
from laborCnt.service.shift_mod_service import ShiftModService
from tornado import gen


class ShiftModModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        """
        处理班次模板创建和修改推送
        :return:
        """
        starttime = datetime.datetime.now()
        req = self.request.body.decode('utf-8')
        infoLog.info('/labor/shiftmod/modify 接口产生调用')
        infoLog.info('req: %s', str(req))

        code, notice = self.check_param(req)
        if code:
            save_result = {'code': 400 + code, 'result': notice}
            self.write(save_result)
            return

        raw_data = json.loads(self.request.body.decode('utf-8'))

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        code, result = check_token(token, time_str)
        if code:
            save_result = {'code': code, 'result': result}
        else:
            save_result = yield ShiftModService.doRequest(raw_data)
        self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'ShiftModModifyHandler'
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

        if 'cid' not in raw_data or 'bid' not in raw_data or 'didArr' not in raw_data or 'opt' not in raw_data:
            return 2, '参数错误，需要包含cid, bid, didArr, opt'

        if raw_data['opt'] != 'update' and raw_data['opt'] != 'delete':
            return 2, 'opt参数错误，需要为update或delete'

        if raw_data['opt'] == 'update':
            if 'shiftModData' not in raw_data:
                return 2, '参数错误，opt为update时需要包含shiftModData'
            shift_mod_data = raw_data['shiftModData']
            for item in shift_mod_data:
                if 'shiftBid' not in item or 'opt' not in item or 'shiftStart' not in item or 'shiftEnd' not in item \
                        or 'isCrossDay' not in item:
                    return 2, 'shiftModData参数错误，需要包含shiftBid, opt, shiftStart, shiftEnd, isCrossDay'
                if item['opt'] != 'update' and item['opt'] != 'delete':
                    return 2, 'shiftModData opt参数错误，需要为update或delete'
        return 0, ''

