#!/usr/bin/env python
# encoding: utf-8

"""
@author: sunsong
@contact: sunsong@didiglobal.com
@file: pushCIs.py
@time: 2019-08-16 16:32
@desc:
"""

import tornado.web
import json
import datetime
import time
from typing import Dict, Tuple
from utils.check_token import check_token
from labor.service.labor_db_service import LaborDbService
from utils.myLogger import infoLog, tracebackLog
from tornado import gen

class PushHandler(tornado.web.RequestHandler):

    def post(self):
        starttime = datetime.datetime.now()
        req = self.request.body.decode('utf-8')
        infoLog.info('PushHandler : %s' % (req.replace('\n', '')))
        code, notice = self.check_param(req)

        if code:
            save_result = {'code': 400+code, 'result': notice}
            self.write(save_result)
            return

        raw_data: Dict = json.loads(self.request.body.decode('utf-8'))

        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')

        code, result = check_token(token, time_str)

        if code:
            save_result = {'code': code, 'result': result}
        else:
            bid = raw_data.get('bid', '')
            operate_type = raw_data.get('operate_type', '')
            mode = raw_data.get('mode', '')
            master_type = raw_data.get('masterType', '')
            slave_type = raw_data.get('slaveType', '')
            delete_bids = raw_data.get('deleteBids', [])
            cid = raw_data.get('cid', '')
            detail_arr = raw_data.get('detailArr', [])
            if operate_type =='delete':
                res = LaborDbService.delete_labor_standard_bids(delete_bids, cid)
            else:
                res1 = LaborDbService.delete_labor_standard_bids([bid], cid)
                res2 =  LaborDbService.update_labor_standard(bid, cid, mode, master_type, slave_type, detail_arr)
                res = 1 if res1!=0 or res2!=0 else 0


            if res == 0:
                save_result = {'code': 100, 'result': '操作成功'}
            elif res == 1:
                save_result = {'code': 408, 'result': 'DB部分操作错误'}
            else:
                save_result = {'code': 400, 'result': '其他错误'}

        self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'PushHandler'
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

        if 'operate_type' in raw_data:
            if raw_data['operate_type'] == 'delete':
                if 'deleteBids' not in raw_data:
                    return 2, 'operate_type为delete时, deleteBids参数必传'
                elif raw_data['deleteBids'] is None:
                    return 3, 'deleteBids是必填字段,不能为空'
                if not ('cid' in raw_data):
                    return 3, '未包含 cid'
            elif raw_data['operate_type'] == 'update':
                if 'bid' in raw_data and 'mode' in raw_data and 'masterType' in raw_data and \
                        'detailArr' in raw_data and 'cid' in raw_data:
                    if raw_data['mode'] !='single':
                        return 2, 'detail参数错误，当前mode只支持single模式'
                    detail_arr = raw_data['detailArr']
                    detail_arr_length = len(detail_arr)
                    if not detail_arr_length:
                        return 2, 'detailArr为空'
                    for detail in detail_arr:
                        if not isinstance(detail, dict):
                            return 2, 'detail格式错误'
                        if 'detailRank' in detail and 'masterTypeScale' in detail and 'worktimeMinute' in detail and 'masterTypeMinScale' in detail:
                            continue
                        else:
                            return 2, 'detail参数错误'
                else:
                    return 2, 'post_json参数错误,需要包含 bid、mode、masterType、detailArr、cid'
            else:
                return 2, 'operate_type参数错误, 只允许delete或update'
        else:
            return 2, '参数错误,operate_type为必传参数'

        return 0, ''
