#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: sch_compliance_service.py
@time: 2020/3/19 10:46
@desc:
'''
from schCompliance.model.sch_compliance_model import SchComplianceModel
from utils.collectionUtils import CollectionUtils
from utils.webResult import WebResult


class SchComplianceService:

    @classmethod
    def list(cls, cid: str, did: int, page: int, size: int):
        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = SchComplianceModel.query(cid, did, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        return WebResult.successData(datas if (datas is not None and len(datas) > 0) else [], count)

    @classmethod
    def select(cls, cid, bidArr):
        if cid is None or len(cid) < 1:
            return WebResult.errorCode(400, "cid is null")

        result = SchComplianceModel.select(cid, bidArr)
        if result is None:
            return WebResult.errorCode(400, "select data error")
        if len(result) < 1:
            return WebResult.successResult("select data is empty")

        datas = []

        bidToItems = CollectionUtils.group(result, "bid")
        for bid in bidToItems:
            items = bidToItems.get(bid)
            ptypeData = []
            data = {
                "cid": None,
                "dids": [],
                "eids": [],
                "bid": None,
                "ptype": None,
                "ptypeData": ptypeData
            }
            datas.append(data)
            for item in items:
                cls.setK(item, data, "cid")
                cls.setK(item, data, "bid")
                cls.setK(item, data, "ptype")
                dids = data.get("dids", [])
                eids = data.get("eids", [])
                did = item.get("did", None)
                eid = item.get("eid", None)
                if did is not None and len(did) > 0:
                    dids.append(did)
                    data["dids"] = dids
                if eid is not None and len(eid) > 0:
                    eids.append(eid)
                    data["eids"] = eids
                ptypeData.append({
                    "ruleType": item.get("ruleType"),
                    "ruleCpType": item.get("ruleCpType"),
                    "ruleCpNum": item.get("ruleCpNum"),
                    "dayFusion": item.get("dayFusion") == None or item.get("dayFusion") == 0,
                    "ruletag": item.get("ruletag"),
                    "cycle": item.get("cycle"),
                    "shiftId": item.get("shiftId"),
                    "cret": item.get("cret"),
                    "timeRange": item.get("timeRange"),
                    "caution": item.get("caution")
                })
        return WebResult.successData(datas)


    @classmethod
    def setK(cls, item, oneItem, param):
        if item is None or oneItem is None:
            return
        oneV = oneItem.get(param, None)
        if oneV is None:
            v = item.get(param, None)
            if v is not None:
                oneItem[param] = v



