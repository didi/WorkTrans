"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ManPowerCls.py
@time: 2019-09-16 11:48
@desc:
"""
from tornado.web import RequestHandler
import json,datetime
from typing import Dict, Tuple
from utils.check_token import check_token
from utils.myLogger import infoLog
from laborCnt.service.labor_task_modify_service import LaborTaskModifyService
from tornado import gen

class LaborTsakModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        infoLog.info('LaborTsakModifyHandler : %s' % (self.request.body.decode('utf-8').replace('\n','')))
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
            save_result = yield LaborTaskModifyService.doRequest(raw_data)
            self.write(save_result)

    @staticmethod
    def check_param(input_json_string: str) -> Tuple[int, str]:
        try:
            raw_data = json.loads(input_json_string)
        except json.JSONDecodeError:
            return 1, 'json解析错误'

        if not isinstance(raw_data, dict):
            return 2, 'json格式错误'

        if 'timestr' not in raw_data or 'token' not in raw_data:
            return 3, '未包含timestr、token'
        elif (raw_data['timestr'] is None) or (raw_data['token'] is None):
            return 3,'timestr、token是必填字段，不能为空'

        if 'cid' not in raw_data or 'taskDetail' not in raw_data:
            return 3, '参数错误,需要包含cid，taskDetail'
        elif (raw_data['cid'] is None) or (raw_data['taskDetail'] is None):
            return 3, 'cid、taskDetail是必填字段，不能为空'
        else:
            for entity in raw_data['taskDetail']:
                if entity['opt'] == 'delete':
                    if 'bid' not in entity:
                        return 2, '参数错误,taskDetail的每条数据需要包含bid'
                    elif entity['bid'] is None:
                        return 2, '参数错误，bid不允许为Null'
                elif entity['opt'] == 'update':
                    if 'taskName' not in entity \
                            or 'bid' not in entity \
                            or 'didArr' not in entity \
                            or 'taskType' not in entity  \
                            or 'worktimeData' not in entity \
                            or 'taskSkill' not in entity \
                            or "certs" not in entity :
                        # 此处，四个新增字段以后取消兼容后释放
                            # or "fillCoefficient" not in entity\
                            # or "discard" not in entity \
                            # or "taskMinWorkTime" not in entity \
                            # or "taskMaxWorkTime" not in entity:
                        return 2, '参数错误,taskDetail的每条数据需要包含taskName,bid,didArr,taskType,worktimeData,taskSkill,certs'

                    if entity['taskName'] is None or entity['taskType'] is None :
                        return 2, '参数错误，taskName、taskType不允许为Null'

                    if entity['taskType'] not in ['directwh', 'indirectwh', 'fixedwh']:
                        return 2, '参数错误,taskType必须在directwh、indirectwh、fixedwh三个值之间'

                    # 此处，四个新增字段以后取消兼容后释放
                    # if entity['discard'] is not None and entity['discard'] not in [1,2]:
                    #     return 2, "参数错误，discard的为1（不可以）或2（可以）"

                    if not isinstance(entity['didArr'], list) \
                            or not isinstance(entity['worktimeData'], list) \
                            or not isinstance(entity['taskSkill'], list) \
                            or not isinstance(entity['certs'], list):
                        return 2, '参数错误,didArr、worktimeData、taskSkill、certs需要为list'

                    for worktime in entity['worktimeData']:
                        if not ("worktimeStart" in worktime and "worktimeEnd" in worktime):
                            return 2, '参数错误 worktimeData中必须存在worktimeStart、wirktimeEnd参数'
                        elif worktime['worktimeType'] is None or worktime['worktimeStart'] is None or worktime[
                            'worktimeEnd'] is None:
                            return 2, '参数错误，worktimeType、worktimeStart、worktimeEnd参数不允许为Null'

                        if 'worktimeType' in worktime and worktime['worktimeType'] not in ['bisTime', 'customTime',
                                                                                           'fixedTime']:
                            return 2, '参数错误,worktimeType必须存在且在bisTime、customTime、fixedTime三个值之间'
                    for skill in entity['taskSkill']:
                        if not ("taskSkillBid" in skill and 'skillNum' in skill):
                            return 2, '参数错误，taskSkill中必须包含taskSkillBid、skillNum参数'
                        elif skill['taskSkillBid'] is None or skill['skillNum'] is None:
                            return 2, '参数错误，taskSkillBid、skillNum不允许为Null'
                else:
                    return 2, '参数错误,opt必须在update、delete两个值之间'

        return 0, ''