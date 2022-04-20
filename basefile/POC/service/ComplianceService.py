"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ComplianceService.py
@time: 2019-10-11 11:24
@desc:
"""
from datetime import datetime
from typing import Dict
from utils.myLogger import infoLog
from POC.model.ComplianceDB import ComplianceDB

class ComplianceService:
    @gen.coroutine
    def doRequest(raw_data:Dict):
        save_result = {'code': 0, 'result': '未处理'}

        cid = str(raw_data["cid"])
        opt = raw_data["opt"]
        ruleData = raw_data["ruleData"]
        # delete
        if opt == "delete":
            # 默认删除成功
            save_result = {'code': 100, 'result': '删除成功'}
            res = ComplianceService.delete_compliance(cid,ruleData)
            if not res:
                save_result = {'code': 101, 'result': '删除失败'}
        # update
        elif opt == 'update':
            res = ComplianceService.delete_compliance(cid,ruleData)
            if not res:
                save_result = {'code': 101, 'result': '更新失败,delete出错'}
                return save_result

            for item in ruleData:
                ptype = item["ptype"]
                bid = item["bid"]
                ptypeData = item.get("ptypeData",[])

                for item2 in ptypeData:
                    ruleType = item2.get("ruleType", '')
                    ruleCpType = item2.get("ruleCpType", '')
                    ruleCpNum = item2.get("ruleCpNum", '')
                    dayFusion = item2.get("dayFusion", '')
                    ruletag = item2.get("ruletag", '')
                    cycle = item2.get("cycle", '')
                    shiftId = item2.get("shiftId", '')
                    cret = item2.get('cert', '')
                    timeRange = item2.get('timeRange', '')
                    startDate = item2.get("startDate", '')
                    caution = item2.get("caution", '')

                    save_result = {'code': 100, 'result': '更新成功'}
                    res_flag = ComplianceDB.update_record(cid, opt, bid, ptype, "", "", ruleType, ruleCpType,
                                                          ruleCpNum, dayFusion, ruletag, cycle, shiftId,
                                                          cret, timeRange, startDate, caution)

                    if not res:
                        save_result = {'code': 101, 'result': '更新失败'}
                        break

            # for item in ruleData:
            #     ptype = item["ptype"]
            #     bid = item["bid"]
            #     if ptype == "organizerule":
            #         # 默认更新成功
            #         save_result = {'code': 100, 'result': '更新成功'}
            #         res = ComplianceService.update_compliance_organizerule(cid,opt,bid,ptype,item)
            #         if not res:
            #             save_result = {'code': 101, 'result': '更新失败'}
            #             break
            #
            #     elif ptype == "emprule":
            #         # 默认更新成功
            #         save_result = {'code': 100, 'result': '更新成功'}
            #         res = ComplianceService.update_compliance_emprule(cid,opt,bid,ptype,item)
            #         if not res:
            #             save_result = {'code': 101, 'result': '更新失败'}
            #             break
        raise gen.Return(save_result)




    @staticmethod
    def delete_compliance(cid,ruleData:list) -> bool:
        res_flag = True
        log_time1 = datetime.now()

        for item in ruleData:
            bid = item['bid']
            res_flag = ComplianceDB.delete_record(cid,bid)
            if not res_flag:
                return res_flag
        log_time2 = datetime.now()
        infoLog.info('ComplianceService delete耗时: ' + str(log_time2 - log_time1))
        return res_flag

    @staticmethod
    def update_compliance_organizerule(cid:str,opt:str,bid:str,ptype:str,ruleDataItem:Dict):
        res_flag = False
        log_time1 = datetime.now()
        didArr = ruleDataItem["didArr"]
        for did in didArr:
            ptypeData = ruleDataItem["ptypeData"]
            for ptdItem in ptypeData:
                ruleType = ptdItem.get("ruleType", '')
                ruleCpType = ptdItem.get("ruleCpType", '')
                ruleCpNum = ptdItem.get("ruleCpNum", '')
                dayFusion = ptdItem.get("dayFusion", '')
                ruletag = ptdItem.get("ruletag", '')
                cycle = ptdItem.get("cycle", '')
                shiftId = ptdItem.get("shiftId", '')
                cret = ptdItem.get('cert', '')
                timeRange = ptdItem.get('timeRange', '')
                startDate = ptdItem.get("startDate", '')
                caution = ptdItem.get("caution", '')
                res_flag = ComplianceDB.update_record(cid,opt,bid,ptype,str(did),"",ruleType,ruleCpType,
                                                      ruleCpNum,dayFusion,ruletag,cycle,shiftId,
                                                      cret,timeRange,startDate,caution)
        log_time2 = datetime.now()
        infoLog.info('ComplianceService update_compliance_organizerule耗时: ' + str(log_time2 - log_time1))
        return res_flag

    @staticmethod
    def update_compliance_emprule(cid:str,opt:str,bid:str,ptype:str,ruleDataItem:Dict):
        res_flag = False
        log_time1 = datetime.now()

        eids = ruleDataItem["eids"]
        for eid in eids:
            ptypeData = ruleDataItem.get("ptypeData",[])
            for ptdItem in ptypeData:
                ruleType = ptdItem.get("ruleType",'')
                ruleCpType = ptdItem.get("ruleCpType",'')
                ruleCpNum = ptdItem.get("ruleCpNum",'')
                dayFusion = ptdItem.get("dayFusion",'')
                ruletag = ptdItem.get("ruletag",'')
                cycle = ptdItem.get("cycle",'')
                shiftId = ptdItem.get("shiftId",'')
                cret = ptdItem.get('cert','')
                timeRange = ptdItem.get('timeRange','')
                startDate = ptdItem.get("startDate",'')
                caution = ptdItem.get("caution",'')

                res_flag = ComplianceDB.update_record(cid, opt, bid,ptype,"", str(eid), ruleType, ruleCpType,
                                                      ruleCpNum, dayFusion, ruletag, cycle, shiftId,
                                                      cret, timeRange, startDate, caution)
        log_time2 = datetime.now()
        infoLog.info('ComplianceService update_compliance_organizerule耗时: ' + str(log_time2 - log_time1))
        return res_flag


if __name__ == '__main__':
        d={"opt":"update","timestr":"2020-07-02 14:04:55.543","ruleData":[{"bid":"2020062912005468614133bfb0000026","ptypeData":[{"ruletag":"shiftTime","ruleCpType":"gt","ruleType":"timerule","dayFusion":False,"ruleCpNum":"480","cycle":"day","caution":"forbid","startDate":"2020-06-01","timeRange":"1"},{"ruletag":"shiftTime","ruleCpType":"lt","ruleType":"timerule","dayFusion":False,"ruleCpNum":"180","cycle":"day","caution":"forbid","startDate":"2020-06-01","timeRange":"1"},{"ruletag":"shiftLen","ruleCpType":"ge","ruleType":"shiftrule","dayFusion":False,"ruleCpNum":"540","cycle":"day","caution":"forbid","startDate":"2020-06-01","timeRange":"1"},{"ruletag":"shiftLen","ruleCpType":"le","ruleType":"shiftrule","dayFusion":False,"ruleCpNum":"60","cycle":"day","caution":"forbid","startDate":"2020-06-01","timeRange":"1"},{"ruletag":"schShiftNum","ruleCpType":"gt","ruleType":"shiftrule","dayFusion":False,"ruleCpNum":"1","cycle":"day","caution":"forbid","startDate":"2020-06-01","timeRange":"1"}],"ptype":"emprule"}],"token":"02d30aa8020f5246bb3e517d14db13f4","cid":50000863}
        print(ComplianceService.doRequest(d))