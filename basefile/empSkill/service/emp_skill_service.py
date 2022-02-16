#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: emp_skill_service.py
@time: 2020/3/20 11:47
@desc:
"""
from typing import List

from empSkill.model.emp_skill_model import EmpSkillModel
from utils.collectionUtils import CollectionUtils
from utils.webResult import WebResult


class EmpSkillService:

    @classmethod
    def list(cls, cid: str, eid: int, page: int, size: int):

        if cid is None or len(cid) < 1:
            return WebResult.errorResult("cid必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = EmpSkillModel.query(cid, eid, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        return WebResult.successData(datas if (datas is not None and len(datas) > 0) else [], count)

    @classmethod
    def select(cls, cid: str, eid_arr: List[int]):
        if cid is None or len(cid) < 1 or eid_arr is None or len(eid_arr) < 1:
            return WebResult.errorCode(400, "cid, eid_arr 必填")

        result = EmpSkillModel.select(cid, eid_arr)
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
        eid_to_item = CollectionUtils.group(result, 'eid')

        if eid_to_item is None:
            return WebResult.errorCode(400, "系统异常")
        return_result = []
        for eid in eid_to_item:
            one_item = {
                "cid": None,
                "eid": None,
                "skills": None
            }
            item_list = eid_to_item.get(eid, None)
            skill_data = []
            if item_list is None:
                continue
            for item in item_list:
                cls.setK(item, one_item, "cid")
                cls.setK(item, one_item, "eid")
                skill_data.append({
                    "skill": item.get("skill", None),
                    "skillNum": item.get("skillNum", None)
                })
            one_item["skills"] = skill_data
            return_result.append(one_item)
        return WebResult.successData(return_result)

    @classmethod
    def setK(cls, item, one_item, param):
        if item is None or one_item is None:
            return
        one_v = one_item.get(param, None)
        if one_v is None:
            v = item.get(param, None)
            if v is not None:
                one_item[param] = v

