"""
by lyy
2019-10-10 17：56
第四阶段接口5 ：员工匹配属性修改
"""

import json, datetime, time
from typing import Tuple, Dict
from tornado.web import RequestHandler
from utils.check_token import check_token
from utils.myLogger import infoLog
from POC.service.EmpMatchpro_Modify_Service import EmpMatchproModifyService
from tornado import gen


class EmpMatchproModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('EmpMatchproModifyHandler : %s' % (self.request.body.decode('utf-8')))
        # 参数检验
        code, notice = EmpMatchproModifyHandler.check_param(self.request.body.decode('utf-8'))
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
            save_result = yield EmpMatchproModifyService.HandleRequest(raw_data)
            self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'EmpMatchproModifyHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

    @staticmethod
    def check_param(input_json_string) -> Tuple[int, str]:
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
            return 3, '未包含token或timestr'
        if 'opt' in raw_data:
            if raw_data['opt'] == 'delete':
                if 'deleteBids' not in raw_data:
                    return 3, '未包含 deleteBids'
                elif raw_data['deleteBids'] is None:
                    return 3, 'deleteBids是必填字段,不能为空'
                if not ('cid' in raw_data):
                    return 3, '未包含cid'
            elif raw_data['opt'] == 'update':
                if not (('cid' in raw_data) or ('didArr' in raw_data) or ('bid' in raw_data)):
                    return 3, '未包含 cid、didArr或bid'
                else:
                    if (raw_data['cid'] is None) or (raw_data['didArr'] is None) or (raw_data['bid'] is None ) :

                        return 3, 'cid、didArr、bid是必填字段,不能为空'
                if not (isinstance(raw_data['didArr'], list)):
                    return 2, 'didArr 不是数组类型'
                if 'matchpros' in raw_data:
                    if not (isinstance(raw_data['matchpros'], list)):
                        return 2, 'matchpros 不是数组类型'
                    else:
                        if len(raw_data['matchpros']) != 0:
                            for item in raw_data['matchpros']:
                                if not (('weight' in item) or ('ruleGroup' in item) or ('ruleCpType' in item) or (
                                        'ruletag' in item)
                                        or ('ruleCpNum' in item)):
                                    return 3, '未包含 weight、ruleGroup、ruleCpType、ruletag、或ruleCpNum'
                                else:
                                    if item['ruleGroup'] not in ['worktime', 'skillcert', 'shiftrule', 'otherrule']:
                                        return 3, 'ruleGroup值必须是worktime,skillcert,shiftrule,otherrule四个中的一个'
                                    if item['ruleCpType'] not in ['lt', 'le', 'eq', 'ge', 'gt']:
                                        return 3, 'ruleCpType值必须是lt, le, eq, ge, gt五个中的一个'
                                    if item['ruletag'] not in ['dayWt', 'monthWt', 'weekWt', 'taskSkilled',
                                                               'positionSkilled', 'positioncert',
                                                               'shiftInterval', 'shiftNum', 'hireAttr', 'agreeOverTime',
                                                               'leadNewPeople']:
                                        return 3, 'ruletag的值必须是dayWt, monthWt, weekWt, taskSkilled, positionSkilled, positioncert, shiftInterval, shiftNum, hireAttr, agreeOverTime, leadNewPeople中的一个'
                                    if (item['weight'] is None) or (item['ruleGroup'] is None) or (
                                            item['ruleCpType'] is None) \
                                            or (item['ruletag'] is None) or (item['ruleCpNum'] is None):
                                        return 3, 'weight、ruleGroup、ruleCpType、ruletag、ruleCpNum是必填字段,不能为空'
                else:
                    return 3, '未包含matchpros'

            else:
                return 3, 'opt值必须是update、delete中的一个'
        else:
            return 3, '未包含opt'

        return 0, ''
