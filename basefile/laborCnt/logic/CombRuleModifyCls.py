#!/usr/bin/env python
# encoding: utf-8

"""
@author: lishulin
@contact: lishulin_i@didiglobal.com
@file: CombRuleModifyCls.py
@time: 2019/9/10 20:49
@desc:
"""
from tornado.web import RequestHandler
import json
import datetime
import time
from typing import List, Dict, Tuple
from utils.check_token import check_token
from utils.myLogger import infoLog
from laborCnt.service.comb_rule_service import CombRuleService
from tornado import gen


class CombRuleModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        req = self.request.body.decode('utf-8')
        infoLog.info('CombRuleModifyHandler: %s' % req)

        #  参数校验
        code, notice = self.check_param(req)
        if code:
            save_result = {'code': 400 + code, 'result': notice}
            infoLog.info('code: %s, result: %s' % (save_result['code'], save_result['result']))
            self.write(save_result)
            return
        infoLog.info('parameter check successfully!')
        raw_data: Dict = json.loads(req)
        infoLog.info('parse json successfully!')
        #  token校验
        time_str = raw_data.get('timestr', '')
        token = raw_data.get('token', '')
        code, result = check_token(token, time_str)
        infoLog.info('check token code: %s, result: %s' % (code, result))

        save_result = None
        if code:
            save_result = {'code': code, 'result': result}
            infoLog.info('code: %s, result: %s' % (save_result['code'], save_result['result']))
        else:
            cid: str = raw_data['cid']
            opt: str = raw_data['opt']
            if opt == 'delete':
                deleteBids = raw_data['deleteBids']
                res = CombRuleService.delete_comb_rule(cid, deleteBids)
                infoLog.info('delete rule: %s' % res)
                if res:
                    save_result = {'code': 100, 'result': '删除成功'}
                else:
                    save_result = {'code': 101, 'result': 'DB操作错误: 删除失败'}
                infoLog.info('code: %s, result: %s' % (save_result['code'], save_result['result']))
            elif opt == 'update':
                bid: str = raw_data['bid']
                did_arr: List[int] = raw_data['didArr']
                rule_data_arr: List = raw_data['combiRuleData']
                rule_data = []
                for rule_dict in rule_data_arr:
                    rule_data.append(rule_dict['ruleData'])
                deleteBids = raw_data['deleteBids']
                res = yield CombRuleService.update_comb_rule(cid, bid, did_arr, rule_data,deleteBids)
                infoLog.info('update rule: %s' % res)
                if res:
                    save_result = {'code': 100, 'result': '更新成功'}
                else:
                    save_result = {'code': 101, 'result': 'DB操作错误: 更新失败'}
                infoLog.info('code: %s, result: %s' % (save_result['code'], save_result['result']))
        self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'CombRuleModifyHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

        return

    def check_param(self, input_json_string) -> Tuple[int, str]:
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

        if not ('cid' in raw_data):
            return 3, '未包含 cid'

        if 'opt' in raw_data:
            if raw_data['opt'] == 'delete':
                if 'deleteBids' not in raw_data:
                    return 3,'删除时，未包含deleteBids'
                elif raw_data['deleteBids'] is None:
                    return 3, '删除时，deleteBids不能为null'
                elif not isinstance(raw_data['deleteBids'], list):
                    return 2,'格式错误，deleteBids不是数组'
                elif len(raw_data['deleteBids']) == 0:
                    return 3, '删除时，deleteBids不能为空列表'
            elif raw_data['opt'] == 'update':
                if not ('didArr' in raw_data and 'bid' in raw_data ):
                    return 3, '未包含didArr 或 bid'
                if not isinstance(raw_data['didArr'], list):
                    return 2, 'didArr不是数组'

                if len(raw_data['didArr']) == 0:
                    return 3, 'didArr为空'
                if 'combiRuleData' in raw_data:
                    if not isinstance(raw_data['combiRuleData'], list):
                        return 2, 'combiRuleData不是数组'
                    elif len(raw_data['combiRuleData']) == 0:
                        return 3, 'combiRuleData为空'
                    else:
                        for rule_data in raw_data['combiRuleData']:
                            if not isinstance(rule_data, dict):
                                return 2, 'ruleData格式错误'
                            if len(rule_data) == 0:
                                return 3, 'combiRuleData中有为NULL的情况'
                            if list(rule_data.keys())[0] != 'ruleData':
                                return 3, 'rule_data key错误'
                else:
                    return 3,'未包含combiRuleData'
            else:
                return 3, 'opt必须为update或delete'

        else:
            return 3,'未包含opt'

        return 0, ''