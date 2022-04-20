
#!/usr/bin/env python
# encoding: utf-8
'''
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: shift_work_inspection_handler.py
@time: 2020/3/13 16:50
@desc:
'''

import json

from shiftWorkInspection.service.shift_work_inspection import ShiftWorkInspectionService
from utils.authenticated import authenticated
from utils.webResult import WebResult
from utils.myLogger import infoLog


class ShiftWorkInspectionHandler(RequestHandler):

    def post(self, route, *args, **kwargs):
        infoLog.info('handler name: %s; route: %s; request body: %s' % (
            str("ShiftWorkInspectionHandler"), str(route), str(self.request.body.decode('utf-8')).replace('\n', '')))
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
        did = req.get("did", None)
        date_str = req.get("date", None)
        return ShiftWorkInspectionService.list(cid, did, date_str)
