#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: employee_certificate_handler.py
@time: 2020/3/20 15:23
@desc:
"""
import json


from employeeCertificate.service.employee_certificate_service import EmployeeCertificateService
from utils.authenticated import authenticated
from utils.webResult import WebResult
from utils.myLogger import infoLog


class EmployeeCertificateHandler(RequestHandler):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
            str("EmployeeCertificateHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
        if route == "list":
            self.write(self.list().__str__())
        else:
            self.write(WebResult.errorCode(404, "请求不存在").__str__())

    @authenticated(role=["滴滴", "喔趣"])
    def list(self):
        """
         {"cid":"123456", "did":1}
        :return:
        """
        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return WebResult.errorResult("json 解析失败")
        cid = req.get("cid", None)
        eid = req.get("eid", None)
        page = req.get("page", None)
        size = req.get("size", None)
        return EmployeeCertificateService.list(cid, eid, page, size)
