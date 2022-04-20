#!/usr/bin/env python
# encoding: utf-8

"""
@author: lishulin
@contact: lishulin_i@didiglobal.com
@file: comb_rule_service.py
@time: 2019/9/10 18:30
@desc:
"""

from typing import List
from laborCnt.model.labor_comb_rule_db import LaborCombRule


class CombRuleService:

    @staticmethod
    def delete_comb_rule(cid: str, deleteBids: List[str]):
        """
        soft delete combination rule
        :param cid: cid
        :param deleteBids: deleteBids
        :return: if succeed
        """
        for bid in deleteBids:
            res = LaborCombRule.soft_delete_record(cid, str(bid))
            if not res:
                return 101
        return 100

    @staticmethod
    @gen.coroutine
    def update_comb_rule(cid: str, bid: str, did_arr: List[int], rule_data_arr: List[str],deleteBids: List[str]):
        """
        update combination rule
        :param cid: cid
        :param bid: bid
        :param did_arr: did_arr
        :param rule_data_arr: rule data arr
        :return: if succeed
        """

        res = LaborCombRule.soft_delete_record(cid, str(bid))
        if not res:
            raise gen.Return(101)

        for bid in deleteBids:
            res = LaborCombRule.soft_delete_record(cid, str(bid))
            if not res:
                raise gen.Return(101)

        for did in did_arr:
            start = True
            for rule in rule_data_arr:
                res = LaborCombRule.update_record(cid, bid, str(did), rule, start=start)
                start = False
                if not res:
                    raise gen.Return(101)
        raise gen.Return(100)

if __name__ == '__main__':
     raw_data={"deleteBids":["2020061917004358214043bb60000088"],"token": "bd839b63f01f70c0687dd4ebe78663b4", "timestr": "2020-06-23 10:46:04.253306","opt":"delete","didArr":[6578,6594,6626,6638,6656,6768,6788,6906,6998,7100,7122,7252,7374,7472,7478],"combiRuleData":[{"ruleData":"2020061518080412614043bb80000369,2020061916572613914043bb60000077,20200403222708138140439830000276,20200403222735621140439830000286,20200403220556919140439830000121,20200403220502266140439830000115,20200403222632806140439830000264"}],"bid":"2020061917004358214043bb60000088","cid":60000039}
     cid:str=raw_data['cid']
     bid: str = raw_data['bid']
     did_arr: List[int] = raw_data['didArr']
     rule_data_arr: List = raw_data['combiRuleData']
     rule_data = []
     for rule_dict in rule_data_arr:
         rule_data.append(rule_dict['ruleData'])
     deleteBids = raw_data['deleteBids']
     print(CombRuleService.update_comb_rule(cid, bid, did_arr, rule_data,deleteBids))