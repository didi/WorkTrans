"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ComplianceHandler.py
@time: 2019-10-11 11:22
@desc:
"""
import json,datetime, time
from typing import Dict, Tuple
from utils.check_token import check_token
from utils.myLogger import infoLog
from POC.service.ComplianceService import ComplianceService

class ComplianceHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        starttime = datetime.datetime.now()
        infoLog.info('ComplianceHandler : %s' % (self.request.body.decode('utf-8').replace('\n','')))
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
            save_result = yield ComplianceService.doRequest(raw_data)
            self.write(save_result)
        endtime = datetime.datetime.now()
        sec = str((endtime - starttime).microseconds)
        handler_name = 'ComplianceHandler'
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

        if 'cid' not in raw_data or 'opt' not in raw_data:
            return 2, '参数错误,需要包含cid，opt'

        if raw_data['cid'] is None or raw_data['opt'] is None:
            return 2, '参数错误,cid、opt不允许为Null'

        if raw_data["opt"] not in ["update","delete"]:
            return 2, "参数错误，opt应为update或delete"

        if raw_data["opt"] == "update" and "ruleData" not in raw_data:
            return 2,"参数错误，缺少ruleData"

        if 'ruleData' not in raw_data:
            return 2, '参数错误,需要包含ruleData'
        else:
            if raw_data.get('ruleData',None) is None:
                return 2,"参数错误，ruleData不允许为空"

            if not isinstance(raw_data['ruleData'],list):
                return 2, "参数错误 ruleData必须是Array"

            for item in raw_data.get("ruleData"):
                if "ptype" not in item or "ptypeData" not in item or "bid" not in item:
                    return 2, "参数错误，ruleData必须包含ptype、ptypeData、bid"

                if item['ptype'] is None or item['ptypeData'] is None:
                    return 2,'参数错误，ptype，ptypeData不允许为Null'

                if item["ptype"] not in ["emprule","organizerule"]:
                    return 2, "参数错误，ptype必须在emprule、organizerule"

                # if item["ptype"] == "organizerule" and len(item.get("didArr",[]))==0:
                #     return 2, "参数错误，ptype值为organizerule，必须包含didArr，且不能为空"

                # if raw_data["opt"] == "update" and item["ptype"] == "emprule" and len(item.get("eids",[]))==0:
                #     return 2, "参数错误，update操作时，ptype值为emprule，必须包含eids，且不能为空"

                if raw_data["opt"] == "update":
                    for item2 in item["ptypeData"]:
                        if  "ruleType" not in item2 or "ruleCpType" not in item2 or "ruletag" not in item2 or "ruleCpNum" not in item2  \
                            or "caution" not in item2 or "startDate" not in item2 or 'dayFusion' not in item2:
                            return 2,"参数错误，update操作时，ptypeData必须包含ruleType、ruleCpType、ruletag、ruleCpNum、caution、startDate、dayFusion"

                        if item2.get('ruleType',None) is None or item2.get('ruleCpType',None) is None or item2.get('ruletag',None) is None or item2.get('ruleCpNum',None) is None\
                            or item2.get('caution',None) is None or item2.get('startDate',None) is None or item2.get('dayFusion',None) is None:
                            return 2,'参数错误，ruleType、ruleCpType、ruletag、ruleCpNum、caution、startDate、dayFusion不允许为Null'

                        if item2["ruleCpType"] not in ['lt','le','eq','ge','gt']:
                            return 2,"releCpType必须在lt、le、eg、ge、gt之间"

                        if item["ptype"] == "emprule" and \
                                item2.get("ruletag","") not in ["shiftTime","shiftLen","interval","schShiftNum",
                                                         "apShiftNum","schDayNumCon","restNumCon","noSchNum",
                                                         "schNumSame","restNum","schCert","certExpireDays"]:
                            return 2, "ptype值为emprule，需要ruletag与之对应"

                        if item["ptype"] == "emprule" and item2.get("ruletag", "") == "apShiftNum" and (item2.get("shiftId","") == ""
                        or item2.get("shiftId","") is None):
                            return 2,"参数错误，ruletag值为apShiftNum时，shiftId必填"

                        if item["ptype"] == "emprule" and item2["ruletag"] == "schCert" and \
                                (item2["ruleCpType"] != "eq" or item2["ruleCpNum"] not in ["0","1"]):
                            return 2,"ptype值为emprule,ruletag值为schCert时，ruleCpNum值为0或1"

                        # if item["ptype"] == "emprule" and item2["ruletag"] == "schCert" and \
                        #         item2["ruleCpType"] == "eq" and item2["ruleCpNum"] == "1" and ("cert" not in item2
                        # or item2.get('cert','') is None):
                        #     return 2, "ptype值为emprule,ruletag值为schCert,ruleCpNum值为1时，必须包含cert"

                        if item["ptype"] == "emprule" and item2["ruletag"] in ["certExpireDays","schCert"]:
                            if "cert" not in item2 or item2.get('cert','') is None:
                                return 2, "ptype值为emprule,ruletag值为schCert或certExpireDays,必须包含cert"

                        if item["ptype"] == "emprule" and item2["ruletag"] != "schCert" and (item2.get("cycle", "") is None
                                or item2.get("timeRange", "") is None):
                            return 2,'当ptype为emprule，ruletag不为schCert时，cycle、timeRange不能为Null'

                        if item2.get("cycle","")!= "" and item2.get("cycle","") not in ["day","week","month"]:
                            return 2,"cycle值应在day、week、month之间"

                        if item2.get("caution","") not in ["hint","forbid","warning"]:
                            return 2,"caution值应在hint、forbid、warning之间"

                        if "ruleType" in item2:
                            if item.get("ptype","")=="emprule" and item2.get("ruleType","") not in ["timerule","shiftrule","daysrule","cretrule"]:
                                return 2,"ptype值为emprule，ruleType应在timerule、shiftrule、daysrule、cretrule之间"

                            if item.get("ptype","")=="organizerule" and item2.get("ruleType","") not in ["skilldemand","cretdemand","shiftdemand"]:
                                return 2,"ptype值为organizerule，ruleType应在skilldemand、cretdemand、shiftdemand之间"

        return 0, ''


if __name__ == '__main__':
    data = {"timestr":"2020-03-05 17:54:17.948","token":"cc30672989cc72ef13179b7bd7cc0949","cid":50000735,"opt":"update","ruleData":[{"ptype":"emprule","bid":"20200227164319361141339020000025","ptypeData":[{"ruletag":"shiftLen","ruleCpType":"lt","ruleType":"shiftrule","dayFusion":False,"ruleCpNum":"60","cycle":"day","caution":"forbid","startDate":"2018-02-01","shiftId":"ruletag=apShiftNum,必填","cert":"证书名称,ruletag为schCert或certExpireDays时必填","timeRange":"1"},{"ruletag":"shiftLen","ruleCpType":"gt","ruleType":"shiftrule","dayFusion":False,"ruleCpNum":"240","cycle":"day","caution":"forbid","startDate":"2020-02-01","shiftId":"ruletag=apShiftNum,必填","cert":"证书名称,ruletag为schCert或certExpireDays时必填","timeRange":"1"},{"ruletag":"certExpireDays","ruleCpType":"ge","ruleType":"shiftrule","dayFusion":False,"ruleCpNum":"60","cycle":"day","caution":"forbid","startDate":"2020-02-01","shiftId":"ruletag=apShiftNum,必填","cert":"证书名称,ruletag为schCert或certExpireDays时必填","timeRange":"1"}]}]}
    res = ComplianceHandler.check_param(data)
    print(res)
