#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: labor_task_service.py
@time: 2020/3/13 13:56
@desc:
'''
import json
from typing import List

from laborTask.model.labor_task import LaborTaskModel
from utils.collectionUtils import CollectionUtils
from utils.webResult import WebResult


class LaborTaskService:

    @classmethod
    def list(cls, cid: str, did: int, page: int, size: int):

        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = LaborTaskModel.query(cid, did, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        return WebResult.successData(datas if (datas is not None and len(datas) > 0) else [], count)

    @classmethod
    def listForBids(cls, cid: str, bids: List):
        """

        :param cid:
        :param bids:
        :return: [{"bids": name}]
        """
        if cid is None or len(cid) < 1 or bids is None or len(bids) < 1:
            return WebResult.errorResult(
              "cid, bids 参数必填"
            )

        lists = LaborTaskModel.listForBids(cid, bids)

        if lists is None:
            return WebResult.errorResult("暂无数据")
        result = {}
        for item in lists:
            if item is None:
                continue
            bid = item.get("bid")
            taskName = item.get("taskName")
            result[bid] = taskName
        return WebResult.successData(result)

    @classmethod
    def listFromBids(cls, cid: str, bids: List):
        """

        :param cid:
        :param bids:
        :return: [{"bids": name}]
        """
        if cid is None or len(cid) < 1 or bids is None or len(bids) < 1:
            return WebResult.errorResult(
                "cid, bids 参数必填"
            )

        lists = LaborTaskModel.listForBids(cid, bids)

        if lists is None:
            return WebResult.errorResult("暂无数据")
        result = {}
        for item in lists:
            if item is None:
                continue
            bid = item.get("bid")
            taskName = item.get("taskName")
            taskType = item.get("taskType")
            result[bid] = {"taskName": taskName, "taskType": taskType}
        return WebResult.successData(result)

    @classmethod
    def select(cls, cid, did, bidArr):
        if cid is None or did is None:
            return WebResult.errorCode(400, "cid or did is null")
        result = LaborTaskModel.select(cid, did, bidArr)
        if result is None:
            return WebResult.errorCode(400, "select data error")
        if len(result) < 1:
            return WebResult.successResult("select data is null")

        bidToItems = CollectionUtils.group(result, "bid")

        datas = []
        for bid in bidToItems:
            items = bidToItems.get(bid)
            if len(items) < 1:
                continue
            _item = items[0]
            task = {
                "cid": _item.get("cid"),
                "did": _item.get("did"),
                "bid": _item.get("bid"),
                "taskName": _item.get("taskName"),
                "abCode": _item.get("abCode"),
                "taskType": _item.get("taskType"),
                "fillCoefficient": _item.get("fillCoefficient"),
                "discard": _item.get("discard"),
                "taskMinWorkTime": _item.get("taskMinWorkTime"),
                "taskMaxWorkTime": _item.get("taskMaxWorkTime")
            }
            worktimeArr = []
            taskSkillArr = []
            certs = []
            for item in items:
                if item is None:
                    continue
                worktimeType = item.get("worktimeType")
                worktimeStart = item.get("worktimeStart")
                worktimeEnd = item.get("worktimeEnd")
                worktimeArr.append(worktime(worktimeType, worktimeStart, worktimeEnd))

                taskSkillBid = item.get("taskSkillBid")
                skillNum = item.get("skillNum")
                taskSkillArr.append(taskSkill(taskSkillBid, skillNum))

                cert = item.get("cert")
                certs.append(cert)
            task["worktimeData"] = cls.getList(worktimeArr)
            task["taskSkill"] = cls.getList(taskSkillArr)
            task["certs"] = list(set(certs))
            datas.append(task)
        return WebResult.successData(datas)

    @classmethod
    def getList(cls, arr):
        items = set(arr)
        result = []
        for item in items:
            dict = {}
            dict.update(item.__dict__)
            result.append(dict)
        return result


class worktime:

    def __init__(self, worktimeType, worktimeStart, worktimeEnd):
        self.worktimeType = worktimeType
        self.worktimeStart = worktimeStart
        self.worktimeEnd = worktimeEnd

    def __hash__(self):
        return hash(self.worktimeType + self.worktimeStart + self.worktimeEnd)

    def __eq__(self, other):
        if self.worktimeType == other.worktimeType \
                and self.worktimeStart == other.worktimeStart and self.worktimeEnd == other.worktimeEnd:
            return True
        else:
            return False


class taskSkill:

    def __init__(self, taskSkillBid, skillNum):
        self.taskSkillBid = taskSkillBid
        self.skillNum = skillNum

    def __hash__(self):
        return hash(self.taskSkillBid + self.skillNum)

    def __eq__(self, other):
        if self.taskSkillBid == other.taskSkillBid \
                and self.skillNum == other.skillNum:
            return True
        else:
            return False


if __name__ == '__main__':
    a = [worktime("bisTime", "08:00", "22:00"), worktime("bisTime", "08:00", "22:01")]
    print(json.dumps(list(set(a))))


