#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: shift_split_rule_service.py
@time: 2020/3/12 16:43
@desc:
'''
from typing import List

from laborShiftSplitRule.model.shift_split_rule_model import ShiftSplitRuleModel
from utils.collectionUtils import CollectionUtils
from utils.webResult import WebResult


class ShiftSplitRuleService:


    @classmethod
    def list(cls, cid: str, did: int, page: int, size: int):

        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = ShiftSplitRuleModel.query(cid, did, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        return WebResult.successData(datas if (datas is not None and len(datas) > 0) else [], count)

    @classmethod
    def select(cls, cid: str, did: str, bidArr: List[str]):
        """
        :param cid:
        :param did:
        :param bidArr:
        :return:
        """

        if cid is None or len(cid) < 1 or did is None or len(did) < 1:
            return WebResult.errorCode(400, "cid, did 必填")

        result = ShiftSplitRuleModel.select(cid, did, bidArr)

        if result is None:
            return WebResult.errorCode(400, "未成功获取数据")

        if len(result) < 1:
            return WebResult.successResult("无数据")

        return cls.transData(result)

    @classmethod
    def transData(cls, result):
        """
        {
    "code": 100,
    "result": "操作成功",
    "data": [{
        "cid": "123456",
        "did": "1029",
        "bid": "201903291236271250271007959f0211",
        "shiftsplitData":[
            {
                "ruleCalType":"interval",
                "ruleCpType":"lt",
                "ruleCpNum":"120",
                "dayFusion":true
            },
            ]
            }]
        :param result:
        :return:
        """
        bidtoItem = CollectionUtils.group(result, 'bid')

        if bidtoItem is None:
            return WebResult.errorCode(400, "系统异常")
        returnResult = []
        for bid in bidtoItem:
            oneItem = {
                "cid": None,
                "did": None,
                "bid": None,
                "shiftsplitData": None
            }
            itemList = bidtoItem.get(bid, None)
            shiftsplitData = []
            if itemList is None:
                continue
            for item in itemList:
                cls.setK(item, oneItem, "cid")
                cls.setK(item, oneItem, "did")
                cls.setK(item, oneItem, "bid")
                shiftsplitData.append({
                    "ruleCalType": item.get("ruleCalType", None),
                    "ruleCpType": item.get("ruleCpType", None),
                    "ruleCpNum": item.get("ruleCpNum", None),
                    "dayFusion": item.get("dayFusion", None)
                })
            oneItem["shiftsplitData"] = shiftsplitData
            returnResult.append(oneItem)
        return WebResult.successData(returnResult)




    @classmethod
    def setK(cls, item, oneItem, param):
        if item is None or oneItem is None:
            return
        oneV = oneItem.get(param, None)
        if oneV is None:
            v = item.get(param, None)
            if v is not None:
                oneItem[param] = v




if __name__ == '__main__':
    req={"timestr":"2020-08-06 18:23:26.729","token":"4d9e05553ab2efad258e1a6d06b07997","did":"5062","cid":"50000127"}
    cid = req.get("cid", None)
    did = req.get("did", None)
    bid_arr = req.get("bidArr", None)
    print(ShiftSplitRuleModel.select(cid, did, bid_arr))



