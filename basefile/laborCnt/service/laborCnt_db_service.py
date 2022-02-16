from laborCnt.model.labor_shift_split_rule_db import LaborShiftSplitRule
import logging
from tornado import gen


class LaborCntDbService:
    @staticmethod
    @gen.coroutine
    def delete_labor_shift_split_rule_db(paramsDict) -> int:
        '''
        软删除
        :return:
        '''
        cid = paramsDict.get('cid', '')
        bid = paramsDict.get('bid', '')

        flag = LaborShiftSplitRule.soft_delete_record(cid, bid)
        if not flag:
            # DB插入失败
            raise gen.Return(101)
        raise gen.Return(100)

    @staticmethod
    @gen.coroutine
    def labor_shift_split_rule_db_modify(parasDict) -> int:
        '''
        修改操作
        :return:
        '''
        cid = parasDict.get('cid','')
        bid = parasDict.get('bid','')
        LaborShiftSplitRule.soft_delete_record(cid, bid)
        didArr = parasDict.get('didArr','')
        for did in didArr:
            opt = parasDict.get('opt','')
            shiftsplitData = parasDict.get('shiftsplitData','')
            for data in shiftsplitData:

                ruleCalType = data.get('ruleCalType','')
                ruleCpType = data.get('ruleCpType','')
                ruleCpNum = data.get('ruleCpNum','')
                dayFusion = data.get('dayFusion','')

                flag = LaborShiftSplitRule.insert_record(cid, bid, did, opt, ruleCalType, ruleCpType, ruleCpNum,dayFusion, 1)
                if not flag:
                    raise gen.Return(101)

        raise gen.Return(100)

if __name__ == '__main__':
    data = {
                "timestr":"2019-09-02 14:26:48.857",
                "token":"6d1059c7f1c4ebb6974065f651a05a2c",
                "cid":"10000",
                "bid":"20190329124156363056100123kg0252",
                "didArr":[
                    7
                ],
                "opt":"delete",
                "shiftsplitData":[
                    {
                        "ruleCalType":"fillCoefficient",
                        "ruleCpType":"lt",
                        "ruleCpNum":"10000",
                        "dayFusion":True
                    },
                    {
                        "ruleCalType":"shiftNum",
                        "ruleCpType":"lt",
                        "ruleCpNum":"10000",
                        "dayFusion":True
                    },
                    {
                        "ruleCalType":"shiftLen",
                        "ruleCpType":"lt",
                        "ruleCpNum":"10000",
                        "dayFusion":True
                    },
                    {
                        "ruleCalType":"worktime",
                        "ruleCpType":"lt",
                        "ruleCpNum":"10000",
                        "dayFusion":True
                    }
                ]
            }

    flag = LaborCntDbService.delete_labor_shift_split_rule_db(data)
    print(flag)



