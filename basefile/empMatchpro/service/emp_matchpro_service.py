#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: emp_matchpro_service.py
@time: 2020/3/19 11:20
@desc:
"""
from empMatchpro.model.emp_matchpro_model import EmpMatchproModel
from utils.webResult import WebResult


class EmpMatchproService:

    @classmethod
    def list(cls, cid: str, did: int, page: int, size: int):

        if cid is None or len(cid) < 1 or did is None:
            return WebResult.errorResult("cid did 必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = EmpMatchproModel.query(cid, did, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        return WebResult.successData(datas if (datas is not None and len(datas) > 0) else [], count)
