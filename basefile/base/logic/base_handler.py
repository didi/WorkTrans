#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: base_handler.py
@time: 2020/3/12 17:40
@desc:
"""

import json


from base.service.base_service import BaseService
from utils.webResult import WebResult
from utils.myLogger import infoLog


class BaseHandler(RequestHandler):
    targets = {
        "shiftsplit": "labor_shift_split_rule",
        "combrule": "labor_comb_rule",
        "task": "labor_task",
        "standard": "labor_standard",
        "laborCacl": "labor_cacl_value",
        "schCompliance": "sch_compliance",
        "empMatchpro": "emp_matchpro",
        "empSkill": "emp_skill",
        "empCertificate": "employee_certificate",
        "schAvTime": "sch_available_time",
        "taskView": "task_matrix_ss",
        "sch": "task_schedule",

    }

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
        str("BaseHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "getCid":
            self.write(self.getCid().__str__())
        elif route == "getDid":
            self.write(self.getDid().__str__())
        elif route == "getEid":
            self.write(self.getEid().__str__())
        else:
            self.write(WebResult.errorCode(404, "请求不存在").__str__())

    def getCid(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        target = req.get("target", None)

        table = self.targets.get(target, None)
        if table is None:
            return WebResult.errorResult("目标不存在")
        return BaseService.getCids(table)

    def getDid(self):
        """
        {"cid":"123456"}
       :return:
       """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        target = req.get("target", None)

        table = self.targets.get(target, None)
        if table is None:
            return WebResult.errorResult("目标不存在")
        cid = req.get("cid", None)
        return BaseService.getDids(table, cid)

    def getEid(self):
        """
                {"cid":"123456"}
               :return:
               """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        target = req.get("target", None)

        table = self.targets.get(target, None)
        if table is None:
            return WebResult.errorResult("目标不存在")
        cid = req.get("cid", None)
        return BaseService.getEids(table, cid)
