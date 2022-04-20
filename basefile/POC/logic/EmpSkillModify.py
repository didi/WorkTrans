"""
by lyy
第四阶段接口二 ：员工技能修改
"""

import json
from typing import Tuple, List, Dict, Any
import datetime,time
from utils.check_token import check_token
from utils.myLogger import infoLog
from POC.service.EmpSkill_Modify_service import EmpSkillModifyService


class EmpSkillModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('EmpSkillModifyHandler : %s' % (self.request.body.decode('utf-8')))
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
            save_result = yield EmpSkillModifyService.HandleRequest(raw_data)
            self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'EmpSkillModifyHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

    def check_param(cls,input_json_string) -> Tuple[int,str]:
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
        elif (raw_data['timestr'] is None) or (raw_data['token'] is None):
            return 3,'timestr、token是必填字段，不能为空'

        if not ( ('cid' in raw_data) or ('skillData' in raw_data)):
            return 3, '未包含 cid 或 skillData'
        elif (raw_data['cid'] is None) or (raw_data['skillData'] is None):
            return 3,'cid、skillData是必填字段，不能为空'

        if not (isinstance(raw_data['skillData'], list)):
            return 2, 'skillData 不是数组类型'

        for p in raw_data['skillData']:
            if not (('eid' in p) or ('opt' in p) or ('skills' in p)):
                return 3,'skillData中未包含 eid 或 opt 或 skills'
            elif (p['eid'] is None) or (p['opt'] is None) or (p['skills'] is None):
                return 3, 'eid、opt、skills是必填字段，不能为空'
            else:
                if p['opt'] == 'update':
                    for s in p['skills']:
                        if not (('skill' in s) or ('skillNum' in s)):
                            return 3, 'skills 中未包含skill 或 skillNum'
                        elif (s['skill'] is None) or (s['skillNum'] is None):
                            return 3, 'skill、skillNum是必填字段，不能为空'

            if not (isinstance(p['skills'],list)):
                return 2,'skills 不是数组类型'
            if p['opt'] != 'update':
                return 3, 'opt只能是update'

        return 0, ''