#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: employee_certificate_service.py
@time: 2020/3/20 15:23
@desc:
"""
from employeeCertificate.model.employee_certificate_model import EmployeeCertificateModel
from utils.webResult import WebResult


class EmployeeCertificateService:

    @classmethod
    def list(cls, cid: str, eid: int, page: int, size: int):

        if cid is None or len(cid) < 1:
            return WebResult.errorResult("cid 必填")
        if page is None or page < 0:
            page = 0
        if size is None or size < 0:
            size = 5

        result = EmployeeCertificateModel.query(cid, eid, page, size)

        if result is None:
            return WebResult.errorResult("查询失败")

        datas = result.get("data", None)
        count = result.get("count", None)

        return WebResult.successData(datas if (datas is not None and len(datas) > 0) else [], count)
