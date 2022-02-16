"""
by lyy
第四阶段接口6 ：获取排班结果
2019-11-11
"""

import json
from typing import Tuple, List, Dict, Any
from tornado.web import RequestHandler,HTTPError
import datetime, time
from utils.check_token import check_token
from utils.myLogger import infoLog
from POC.service.PBStatusService import PBStatusService

from tornado import gen

class PBResultHandler(RequestHandler):

    # 记录异常
    _reason = None

    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('PBResultHandler : %s' % (self.request.body.decode('utf-8').replace('\n','')))
        s = datetime.datetime.now()
        save_result = None

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
        else:

            try:

                save_result_l = yield  PBStatusService.doRequest(raw_data)

                save_result = {'code': 100, 'result': '操作成功', 'data':save_result_l.get('data')}
                print('end')
                print(save_result_l.get('data'))
            except Exception as result:
                print(result)
                PBResultHandler._reason = str(result)

        self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'PBResultHandler'
        timestr = time.mktime(starttime.timetuple())
        infoLog.info('handler_name: %s, timestrs: %s, starttime: %s,  endtime: %s, endtime-starttime: %s ms', handler_name, str(timestr), str(starttime), str(endtime), sec)

    def write_error(self, status_code, **kwargs):
        '''
        自定义错误代码返回
        :param status_code:
        :param kwargs:
        :return:
        '''
        if status_code == 500:
            self.write("<html><title>%(code)d: %(message)s</title>"
                    "<body>%(code)d: %(message)s</body></html>" % {
                        "code": status_code,
                        "message": PBResultHandler._reason,
                    })
            self.finish()

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

        if 'cid' not in raw_data or 'applyId' not in raw_data \
                or "didArr" not in raw_data or "start" not in raw_data\
                or "end" not in raw_data or "schType" not in raw_data\
                or "scheme" not in raw_data or "emps" not in raw_data\
                or 'recalculation' not in raw_data\
                or 'calRelyon' not in raw_data or 'accessToken' not in raw_data or 'callbackUrl' not in raw_data:
            return 3, '参数错误,需要包含cid,applyId,didArr,start,end,schType,scheme,emps,recalculation,calRelyon,accessToken'

        if raw_data['schType'] not in ['0','1','2']:
            return 3, '参数错误,schType必须取0，1，2中的某个'


        if raw_data.get('calRelyon','wtForecast') not in ['wtForecast','mpForecast']:
            return 3, '参数错误，calRelyon值为wtForecast或mpForecast'

        if not isinstance(raw_data.get("recalculation",False),bool):
            return 3,'参数错误，recalculation需要为bool类型'

        if not isinstance(raw_data.get("didArr",""),list):
            return 3, "参数类型错误，didArr必须是一个Array"

        if not isinstance(raw_data.get("emps",""),list):
            return 3, "参数类型错误，emps必须是一个Array"

        for item in raw_data.get("emps",""):
            if ("eid" not in item) :
                return 3, "参数错误，emps必须包含eid"

            # if item['isNew'] not in ['yes','no']:
            #     return 3,'参数错误，isNew的值必须是yes,no中的一个'
            #
            # if item['hireType'] not in ['full','part']:
            #     return 3,'参数错误，hireType 的值必须是full,part中的一个'
            #
            # if item['agreeOverTime'] not in ['yes','no']:
            #     return 3,'参数错误，agreeOverTime 的值必须是yes,no中的一个'
            #
            # if item['leadNew'] not in ['yes','no']:
            #     return 3,'参数错误，leadNew 的值必须是yes,no中的一个'

            if "specialTime" in item:
                if not isinstance(item.get("specialTime", ""), list):
                    return 3, "参数类型错误，specialTime必须是一个Array"

                for item2 in item.get("specialTime", ""):
                    if "startTime" not in item2 or "endTime" not in item2:
                        return 3,"specialTime必须包含start、end"
        return 0, ''