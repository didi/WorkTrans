#!/usr/bin/env python
# encoding: utf-8
"""
@author: sean
@contact: kangshenzhen@woqukaoqin.com
@file: base_service.py
@time: 2020/3/12 16:36
@desc:
"""
from base.model.base_model import BaseModel
from utils.webResult import WebResult


class BaseService:

    @classmethod
    def getCids(cls, table: str):
        cids = BaseModel.getCid(table)
        if cids is None:
            return WebResult.errorResult("cid 查询失败")
        data = []
        for item in cids:
            if item is None:
                continue
            cid = item['cid']
            if cid is None or len(cid) == 0:
                continue
            data.append(cid)
        return WebResult.successData(data)

    @classmethod
    def getDids(cls, table: str, cid: str):
        dids = BaseModel.getDids(cid, table)
        if dids is None:
            return WebResult.errorResult("did 查询失败")
        data = []
        for item in dids:
            if item is None:
                continue
            did = item['did']
            if did is None or len(did) == 0:
                continue
            data.append(did)
        return WebResult.successData(data)

    @classmethod
    def getEids(cls, table: str, cid: str):
        dids = BaseModel.getEids(cid, table)
        if dids is None:
            return WebResult.errorResult("did 查询失败")
        data = []
        for item in dids:
            if item is None:
                continue
            eid = item['eid']
            if eid is None or len(eid) == 0:
                continue
            data.append(eid)
        return WebResult.successData(data)
