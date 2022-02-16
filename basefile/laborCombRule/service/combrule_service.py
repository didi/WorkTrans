#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: combrule_service.py
@time: 2020/3/13 10:32
@desc:
'''
from typing import List

from laborCombRule.model.combrule_model import CombruleModel
from laborTask.service.labor_task_service import LaborTaskService
from utils.collectionUtils import CollectionUtils
from utils.webResult import WebResult


class CombruleService:


    @classmethod
    def list(cls, cid: str, did: int, page: int, size: int):

        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = CombruleModel.query(cid, did, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        datas = datas if (datas is not None and len(datas) > 0) else []
        _taskBids = []
        for data in datas:
            taskBid = data.get("rule_data")
            _taskBids.append(taskBid)

        taskBids = ",".join(_taskBids).split(",")
        taskBids = list(set(taskBids))

        bidtoNameResult = LaborTaskService.listForBids(cid, taskBids)
        bidtoName = {}
        if bidtoNameResult.isSuccess:
            bidtoName = bidtoNameResult.data
        for data in datas:
            taskBid = data.get("rule_data")
            if taskBid is None:
                continue
            taskBids = taskBid.split(",")
            taskName = []
            for taskbid in taskBids:
               name = bidtoName.get(taskbid, None)
               if name is None:
                   name = taskbid
               taskName.append(name)
            data["taskName"] = ",".join(taskName)

        return WebResult.successData(datas, count)

    @classmethod
    def select(cls, cid: str, did: int, bidArr: List[str]):
        """
        :param cid:
        :param did:
        :param bidArr:
        :return:
        """
        if cid is None or len(cid) < 1 or did is None or len(did) < 1:
            return WebResult.errorCode(400, "cid, did 必填")

        result = CombruleModel.select(cid, did, bidArr)
        if result is None:
            return WebResult.errorCode(400, "未成功获取数据")

        if len(result) < 1:
            return WebResult.successResult("无数据")

        return cls.transData(result)

    @classmethod
    def transData(cls, result):
        """

        :param result:
        :return:
        """
        # FIXME 此方法支持是单个部门数据，如果多部门的话另行修改
        bidtoItem = CollectionUtils.group(result, 'bid')

        if bidtoItem is None:
            return WebResult.errorCode(400, "系统异常")
        returnResult = []
        for bid in bidtoItem:
            oneItem = {
                "cid": None,
                "did": None,
                "bid": None,
                "combiRuleData": None
            }
            itemList = bidtoItem.get(bid, None)
            combiRuleData = []
            if itemList is None:
                continue
            for item in itemList:
                cls.setK(item, oneItem, "cid")
                cls.setK(item, oneItem, "did")
                cls.setK(item, oneItem, "bid")
                combiRuleData.append({
                    "ruleData": item.get("rule_data", None),
                })
            oneItem["combiRuleData"] = combiRuleData
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






