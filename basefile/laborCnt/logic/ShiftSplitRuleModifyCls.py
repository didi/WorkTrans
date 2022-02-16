"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ShiftSplitRuleModifyCls.py
@time: 2019-09-09 16:14
@desc:
"""
from tornado.web import RequestHandler
import json,datetime
from typing import Dict, Tuple
from utils.check_token import check_token
from utils.myLogger import infoLog
from laborCnt.service.laborCnt_db_service import LaborCntDbService
from tornado import gen

class ShiftSplitRuleModifyHandler(RequestHandler):

    @gen.coroutine
    def post(self):
        infoLog.info('ShiftSplitRuleModifyHandler : %s' % (self.request.body.decode('utf-8')))
        s = datetime.datetime.now()
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
            if notice == 'delete':
                code = yield LaborCntDbService.delete_labor_shift_split_rule_db(raw_data)
            elif notice == 'update':
                code = yield LaborCntDbService.labor_shift_split_rule_db_modify(raw_data)

            if code == 100:
                e = datetime.datetime.now()
                infoLog.info('ShiftSplitRuleModifyHandler...此次请求耗时%s' % (e - s))
                self.write({'code': 100, 'result': '处理成功'})
            elif code == 101:
                e = datetime.datetime.now()
                infoLog.info('ShiftSplitRuleModifyHandler...此次请求耗时%s' % (e - s))
                self.write({'code': 101, 'result': 'DB操作错误'})
            else:
                e = datetime.datetime.now()
                infoLog.info('ShiftSplitRuleModifyHandler...此次请求耗时%s' % (e - s))
                self.write({'code': 400, 'result': '其他错误'})




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
            return 3, '未包含token'

        if not ( 'cid' in raw_data or 'bid' in raw_data  or 'didArr' in raw_data):
            return 2, '未包含 cid 、bid 或 didArr'

        if not (isinstance(raw_data['didArr'], list)):
            return 2, 'didArr不是数组'

        if raw_data['opt'] not in ['update','delete']:
            return 2,'opt必须在update、delete两个值之间'

        ## opt = delete and shiftsplitDatq is null
        if raw_data['opt'] == 'delete':
            return 0, 'delete'
        elif 'shiftsplitData' not in raw_data and raw_data['opt'] == 'update':
            return 2,'修改操作未包含shiftsplitData'

        for d in raw_data['shiftsplitData']:
            if not ("ruleCpType" in d or "ruleCpNum" in d or "dayFusion" in d):
                return 2, 'shiftsplitData 必须包含[ruleCpType、ruleCpNum、dayFusion]'

            if (d['ruleCalType'] is not None) and (d['ruleCalType'] not in ['interval','shiftNum','shiftLen','worktime','fillCoefficient','taskCount']):
                return 2, 'ruleCalType interval、shiftNum、shiftLen、worktime四个值之间'

            # lt, le, eq, ge, gt。小于，小于等于，等于， 大于等于，大于
            if d['ruleCpType'] not in ['lt','le','eq','ge','gt']:
                return 2, 'ruleCalType interval、shiftNum、shiftLen、worktime四个值之间'

        return 0, 'update'