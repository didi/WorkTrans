#!/usr/bin/env python
# encoding: utf-8

"""
@author: sean
@file: base_goods_task.py
@time: 2020/02/26 14:18
@desc: 预测每15 分钟预测量 service
"""
import copy
import random
import string
from datetime import datetime, timedelta
import json

from utils.dateUtils import DateUtils
from viewGoodsDf.model.view_goods_model import ViewGoodsModel


class ViewGoodsService:

    @staticmethod
    def doRequest(raw_data):
        # 需要事务回滚
        # 检查参数， 数据插入（有就插入，没有更新）
        save_result = {'code': 0, 'result': '未处理'}
        if len(raw_data) < 1:
            return save_result
        # 上层数据校验
        updateDataType = raw_data.get("updateDataType", [])
        datas = raw_data.get("datas", None)
        if datas is None or len(updateDataType) < 1:
            return save_result
        insert = {}
        update = {}
        # 是否是真实值更新
        isTrue = 'true' in updateDataType

        # 是否是修改预测值
        isPredict = 'predict' in updateDataType

        # 是否是手动修改值
        isAdjust = 'adjust' in updateDataType

        alerdQuery = []
        uktoobj = {}

        for data in datas:
            cid = data.get("cid", None)
            did = data.get("did", None)
            goodsBid = data.get("goods_bid", None)
            day = data.get("day", None)

            time = data.get("time", None)
            price = data.get("price", None)
            trueSingleSale = data.get("trueSingleSale", None)
            predictSingleSale = data.get("predictSingleSale", None)
            adjustSingleSale = data.get("adjustSingleSale", None)
            trueGMV = data.get("trueGMV", None)
            predictGMV = data.get("predictGMV", None)
            adjustGMV = data.get("adjustGMV", None)

            trueOrders = data.get("trueOrders", None)
            predictOrders = data.get("predictOrders", None)
            adjustOrders = data.get("adjustOrders", None)

            truePeoples = data.get("truePeoples", None)
            predictPeoples = data.get("predictPeoples", None)
            adjustPeoples = data.get("adjustPeoples", None)

            hourAndMinute = DateUtils.get_new_time_15_minute(time)

            if hourAndMinute is None:
                continue
            hour = hourAndMinute[0]
            minute = hourAndMinute[1]

            shike = day + " " + ViewGoodsService.trfHourAndMin(hour) + ":" + ViewGoodsService.trfHourAndMin(minute)

            # 查询数据是否存在， 只查询一次
            query = cid + str(did) + day
            if query not in alerdQuery:
                list = ViewGoodsService.list(cid, did, None, day)
                _uktoobj = trans_key_to_obj(list)
                if _uktoobj is not None:
                    uktoobj.update(_uktoobj)
                alerdQuery.append(query)

            key = cid + str(did) + goodsBid + shike
            uktoobj = {}
            if uktoobj.get(key, None) is None:
                # 新增
                viewGoodsMode = insert.get(key, None)
                viewGoodsMode = ViewGoodsService.calModel(cid, did, goodsBid, trueSingleSale, predictSingleSale,
                                                          adjustSingleSale, trueGMV, adjustGMV,
                                                          predictGMV, trueOrders, predictOrders, adjustOrders,
                                                          truePeoples, predictPeoples, adjustPeoples, price,
                                                          shike, viewGoodsMode, isAdjust, isPredict, isTrue)
                insert[key] = viewGoodsMode
            else:
                # 更新
                upViewGoodsMode = update.get(key, None)
                upViewGoodsMode = ViewGoodsService.calModel(cid, did, goodsBid, trueSingleSale, predictSingleSale,
                                                            adjustSingleSale, trueGMV, adjustGMV,
                                                            predictGMV, trueOrders, predictOrders, adjustOrders,
                                                            truePeoples, predictPeoples, adjustPeoples, price,
                                                            shike, upViewGoodsMode, isAdjust, isPredict, isTrue)
                update[key] = upViewGoodsMode

        # 事务回滚
        return ViewGoodsService.saveOrUpdate(insert, update, isTrue, isPredict, isAdjust)

    @staticmethod
    def list(cid: str, did: int, goods_bid: str, shike: str):
        result = ViewGoodsModel.list(cid, did, goods_bid, shike)
        return result

    @classmethod
    def listByShikes(cls, cid: str, did: int, goodsBid: str, shikes, page: int, size: int):
        """
               :param cid: 必填
               :param did: 必填
               :param goodsBid: 可以不填
               :param shikes: shike 必填   [yyyy-MM-dd hh:mm] 格式
               :return:
               """

        if len(cid) < 1 or did is None or len(shikes) < 1:
            return None

        result = ViewGoodsModel.listByShikes(cid, did, goodsBid, shikes, page, size)

        return result

    @classmethod
    def listByShike(cls, cid: str, did: int, goodsBid: str, startShike: str, endShike: str, isComplete: bool, page: int, size: int):

        """
        :param cid: 必填
        :param did: 必填
        :param goodsBid: 可以不填
        :param startShike: 开始 必填    开始或结束：支持  yyyy-MM-dd  也支持 yyyy-MM-dd hh:mm 格式
        :param endShike: 结束 必填
        :param isComplete: 是否补全数据  比如 数据库当天只有  10：30 得数据 其它得时间相隔15 分钟得数据都会补全， 数据全部是 0
        :return:
        """

        if len(cid) < 1 or did is None or len(startShike) < 1 or len(endShike) < 1:
            return None

        result = ViewGoodsModel.listByShike(cid, did, goodsBid, startShike, endShike, page, size)

        if result is None:
            return None

        if not isComplete:
            return result

        # 查询出来 但是缺得数据补全
        # 先按goodsBid 分类 # FIXME: 如果有合适得分组工具方法替换
        allList = ViewGoodsService.complete(endShike, result, startShike)

        return allList

    @classmethod
    def complete(cls, endShike, result, startShike):
        goodsBidToList = {}
        for data in result:
            goodsBid = data.get("goods_bid")
            hasData = goodsBidToList.get(goodsBid, [])
            hasData.append(data)
            goodsBidToList[goodsBid] = hasData
        start = datetime.strptime(ViewGoodsModel.getShike(startShike, True), '%Y-%m-%d %H:%M')
        end = datetime.strptime(ViewGoodsModel.getShike(endShike, False), '%Y-%m-%d %H:%M')
        allList = []
        for key in goodsBidToList:
            items = goodsBidToList.get(key)
            items.sort(key=lambda x: x["shike"])

            map = {}
            temp = None
            for item in items:
                map[item["shike"]] = item
                if temp is None:
                    temp = item;
            _start = start
            while end > _start:

                key = _start.strftime("%Y-%m-%d %H:%M")

                value = map.get(key, None)

                if value is None:
                    newDefault = ViewGoodsService.getDefault(temp, key)
                    allList.append(newDefault)
                else:
                    allList.append(value)

                _start = _start + timedelta(minutes=15)
        return allList

    @classmethod
    def saveOrUpdate(cls, insert, update, isTrue: bool, isPredict: bool, isAdjust: bool):
        if insert is not None and len(insert) > 0:
            for key in insert:
                viewGoodsMode = insert.get(key)

                result = ViewGoodsModel.insertObj(viewGoodsMode)
                if result == False:
                    return {'code': 1, 'result': '保存失败'}
        if update is not None and len(update) > 0:
            for key in update:
                updateviewGoodsMode = update.get(key)
                # 本次更新不能更新状态
                updateviewGoodsMode["status"] = None
                if not isTrue:
                    updateviewGoodsMode["trueSingleSale"] = None
                    updateviewGoodsMode["trueGMV"] = None
                if not isPredict:
                    updateviewGoodsMode["predictSingleSale"] = None
                    updateviewGoodsMode["predictGMV"] = None
                if not isAdjust:
                    updateviewGoodsMode["adjustSingleSale"] = None
                    updateviewGoodsMode["adjustGMV"] = None
                updateResult = ViewGoodsModel.updateObj(updateviewGoodsMode)
                if not updateResult:
                    return {'code': 1, 'result': '更新失败'}

        return {'code': 0, 'result': '操作成功'}

    @classmethod
    def getDefault(cls, item, key):
        if item is None or len(item) < 1:
            return None

        result = copy.deepcopy(item)

        result["true_single_sale"] = 0
        result["predict_single_sale"] = 0
        result["adjust_single_sale"] = 0
        result["true_gmv"] = 0.0
        result["predict_gmv"] = 0.0
        result["adjust_gmv"] = 0.0
        result["shike"] = key
        # 如果有orders 设置orders
        return result

    @classmethod
    def calModel(cls, cid, did, goodsBid, trueSingleSale, predictSingleSale, adjustSingleSale, trueGMV, adjustGMV,
                 predictGMV, trueOrders, predictOrders, adjustOrders, truePeoples, predictPeoples, adjustPeoples, price,
                 shike, viewGoodsMode, isAdjust, isPredict, isTrue):
        if viewGoodsMode is None:
            viewGoodsMode = ViewGoodsService.getModel(cid, did, goodsBid, price, shike, trueSingleSale,
                                                      predictSingleSale, adjustSingleSale, trueGMV, predictGMV,
                                                      adjustGMV, trueOrders, predictOrders,
                                                      adjustOrders, truePeoples, predictPeoples,
                                                      adjustPeoples, isTrue, isPredict, isAdjust)
        else:
            _trueSingleSale = viewGoodsMode.get("trueSingleSale", 0)
            _predictSingleSale = viewGoodsMode.get("predictSingleSale", 0)
            _adjustSingleSale = viewGoodsMode.get("adjustSingleSale", 0)
            _trueGMV = viewGoodsMode.get("trueGMV", 0.0)
            _predictGMV = viewGoodsMode.get("predictGMV", 0.0)
            _adjustGMV = viewGoodsMode.get("adjustGMV", 0.0)

            _trueOrders = viewGoodsMode.get("trueOrders", 0)
            _predictOrders = viewGoodsMode.get("predictOrders", 0)
            _adjustOrders = viewGoodsMode.get("adjustOrders", 0)

            _truePeoples = viewGoodsMode.get("truePeoples", 0)
            _predictPeoples = viewGoodsMode.get("predictPeoples", 0)
            _adjustPeoples = viewGoodsMode.get("adjustPeoples", 0)

            viewGoodsMode["trueSingleSale"] = int(_trueSingleSale) + int(trueSingleSale)
            viewGoodsMode["predictSingleSale"] = int(_predictSingleSale) + int(predictSingleSale)
            viewGoodsMode["adjustSingleSale"] = int(_adjustSingleSale) + int(adjustSingleSale)
            viewGoodsMode["trueGMV"] = float(_trueGMV) + float(trueGMV)
            viewGoodsMode["predictGMV"] = float(_predictGMV) + float(predictGMV)
            viewGoodsMode["adjustGMV"] = float(_adjustGMV) + float(adjustGMV)

            viewGoodsMode["trueOrders"] = int(_trueOrders) + int(trueOrders)
            viewGoodsMode["predictOrders"] = int(_predictOrders) + int(predictOrders)
            viewGoodsMode["adjustOrders"] = int(_adjustOrders) + int(adjustOrders)

            viewGoodsMode["truePeoples"] = int(_truePeoples) + int(truePeoples)
            viewGoodsMode["predictPeoples"] = int(_predictPeoples) + int(predictPeoples)
            viewGoodsMode["adjustPeoples"] = int(_adjustPeoples) + int(adjustPeoples)

        return viewGoodsMode

    @classmethod
    def getModel(cls, cid: str, did: int, goodsBid: str, price, shike: str, trueSingleSale: int, predictSingleSale: int,
                 adjustSingleSale: int, trueGMV, predictGMV, adjustGMV, trueOrders: int, predictOrders: int,
                 adjustOrders: int, truePeoples: int, predictPeoples: int,
                 adjustPeoples: int, isTrue: bool, isPredict: bool, isAdjust: bool):

        model = {
            "cid": cid,
            "goods_bid": goodsBid,
            "price": float(price),
            "shike": shike,
            "did": did,
            "status": 1,
            "trueSingleSale": trueSingleSale,
            "predictSingleSale": predictSingleSale,
            "adjustSingleSale": adjustSingleSale,
            "trueGMV": float(trueGMV),
            "predictGMV": float(predictGMV),
            "adjustGMV": float(adjustGMV),
            "trueOrders": trueOrders,
            "predictOrders": predictOrders,
            "adjustOrders": adjustOrders,
            "truePeoples": truePeoples,
            "predictPeoples": predictPeoples,
            "adjustPeoples": adjustPeoples
        }
        return model

    @classmethod
    def trfHourAndMin(cls, hourOrMin: int) -> str:
        if hourOrMin < 9:
            return "0" + str(hourOrMin)
        return str(hourOrMin)

    @classmethod
    def getCid(cls):
        cids = ViewGoodsModel.getCid()
        return cids

    @classmethod
    def getDid(cls, cid: str):
        if cid is None or len(cid) < 1:
            return None

        dids = ViewGoodsModel.getDids(cid)
        return dids

    @classmethod
    def getGoodsBids(cls, cid, did):
        if cid is None or len(cid) < 1 or did is None or did < 1:
            return None

        bids = ViewGoodsModel.getBids(cid, did)
        return bids


def trans_key_to_obj(list):
    if list is None or len(list) < 1:
        return None
    result = {}
    for obj in list:
        cid = obj.get("cid", None)
        goods_bid = obj.get("goods_bid", None)
        did = obj.get("did", None)
        shike = obj.get("shike", None)
        if cid is None or goods_bid is None or did is None or shike is None:
            continue
        key = cid + str(did) + goods_bid + shike
        result[key] = obj

    return result


if __name__ == '__main__':
    data = []

    i = 0
    did = 1
    _start = datetime.strptime("2020-03-01", '%Y-%m-%d')
    while i < 1000:


        _start = _start + timedelta(minutes=15)
        day = datetime.strftime(_start, '%Y-%m-%d')
        time = datetime.strftime(_start, ' %H:%M:%S')
        hour = _start.hour


        if i > 300 and i < 600:
            did = 2
        if i >= 600:
            did = 3


        goods_name = ['汉堡bid', '薯条', '奶茶', '果汁', '炸鸡', '披萨', '翅根', '全家桶', '随便', '烤鸡']
        index = random.randint(0, len(goods_name) - 1)

        singSale = random.randint(500, 800)
        predictsingSale = random.randint(650, 750)
        adjustsingSale = random.randint(700, 800)
        trueOrders = random.randint(10, 30)
        predictOrders = random.randint(15, 25)
        adjustOrders = random.randint(12, 27)
        truePeoples = random.randint(10, 50)
        predictPeoples = random.randint(17, 48)
        adjustPeoples = random.randint(20, 30)

        if (hour > 11 and hour < 13) or (hour > 17 and hour < 20):
            # 高峰期
            singSale = random.randint(700, 1200)
            predictsingSale = random.randint(1000, 1500)
            adjustsingSale = random.randint(900, 1200)
            trueOrders = random.randint(20, 50)
            predictOrders = random.randint(25, 35)
            adjustOrders = random.randint(22, 37)
            truePeoples = random.randint(30, 50)
            predictPeoples = random.randint(30, 50)
            adjustPeoples = random.randint(30, 50)
        if (hour > 0 and hour < 8) or (hour > 22 and hour < 24):
            # 高峰期
            singSale = random.randint(0, 200)
            predictsingSale = random.randint(0, 150)
            adjustsingSale = random.randint(0, 170)
            trueOrders = random.randint(0, 10)
            predictOrders = random.randint(0, 15)
            adjustOrders = random.randint(0, 12)
            truePeoples = random.randint(0, 10)
            predictPeoples = random.randint(0, 12)
            adjustPeoples = random.randint(0, 10)

        data.append({
                "cid": "123456",
                "did": did,
                "goods_bid": goods_name[index],
                "day": day,
                "time": str.strip(time),
                "price": "12.5",
                "trueSingleSale": singSale,
                "predictSingleSale": predictsingSale,
                "adjustSingleSale": adjustsingSale,
                "trueGMV": singSale,
                "predictGMV": predictsingSale,
                "adjustGMV": adjustsingSale,
                "trueOrders": trueOrders,
                "predictOrders": predictOrders,
                "adjustOrders": adjustOrders,
                "truePeoples": truePeoples,
                "predictPeoples": predictPeoples,
                "adjustPeoples": adjustPeoples
            })
        i += 1
    print(json.dumps(data))


    raw_data = {
        "updateDataType": ["true", "predict", "adjust"],  # 操做类型， 一般只有一个支持多个 "true", "predict", "adjust"
        "datas": data
    }
    print(ViewGoodsService.doRequest(raw_data))
    # print(json.dumps(ViewGoodsService.listByShike("123456",1, '123456', "2020-02-27 09:00", "2020-02-28 12:00", True)))

    # jsonD = "{'123456': [{'audo_id': 102, 'insert_time': datetime.datetime(2020, 2, 29, 17, 43, 12), 'update_time': datetime.datetime(2020, 2, 29, 17, 43, 12), 'status': 1, 'cid': '123456', 'shike': '2020-02-27 10:00', 'goods_bid': '123456', 'did': 1, 'price': 12.5, 'true_single_sale': 200, 'predict_single_sale': 10000, 'adjust_single_sale': 0, 'true_gmv': 250.5, 'predict_gmv': 0.0, 'adjust_gmv': 0.0, 'true_orders': 0, 'predict_orders': 0, 'adjust_orders': 0}, {'audo_id': 105, 'insert_time': datetime.datetime(2020, 2, 29, 17, 43, 12), 'update_time': datetime.datetime(2020, 2, 29, 17, 43, 12), 'status': 1, 'cid': '123456', 'shike': '2020-02-27 10:15', 'goods_bid': '123456', 'did': 1, 'price': 24.0, 'true_single_sale': 1010, 'predict_single_sale': 0, 'adjust_single_sale': 0, 'true_gmv': 2500.0, 'predict_gmv': 0.0, 'adjust_gmv': 0.0, 'true_orders': 0, 'predict_orders': 0, 'adjust_orders': 0}, {'audo_id': 107, 'insert_time': datetime.datetime(2020, 2, 29, 17, 43, 13), 'update_time': datetime.datetime(2020, 2, 29, 17, 43, 13), 'status': 1, 'cid': '123456', 'shike': '2020-02-27 10:30', 'goods_bid': '123456', 'did': 1, 'price': 12.5, 'true_single_sale': 10, 'predict_single_sale': 0, 'adjust_single_sale': 0, 'true_gmv': 1250.0, 'predict_gmv': 0.0, 'adjust_gmv': 0.0, 'true_orders': 0, 'predict_orders': 0, 'adjust_orders': 0}, {'audo_id': 108, 'insert_time': datetime.datetime(2020, 2, 29, 17, 43, 13), 'update_time': datetime.datetime(2020, 2, 29, 17, 43, 13), 'status': 1, 'cid': '123456', 'shike': '2020-02-27 10:45', 'goods_bid': '123456', 'did': 1, 'price': 12.5, 'true_single_sale': 10, 'predict_single_sale': 0, 'adjust_single_sale': 0, 'true_gmv': 1250.0, 'predict_gmv': 0.0, 'adjust_gmv': 0.0, 'true_orders': 0, 'predict_orders': 0, 'adjust_orders': 0}], '12345622': [{'audo_id': 103, 'insert_time': datetime.datetime(2020, 2, 29, 17, 43, 12), 'update_time': datetime.datetime(2020, 2, 29, 17, 43, 12), 'status': 1, 'cid': '123456', 'shike': '2020-02-27 10:00', 'goods_bid': '12345622', 'did': 1, 'price': 12.5, 'true_single_sale': 100, 'predict_single_sale': 10000, 'adjust_single_sale': 0, 'true_gmv': 125.5, 'predict_gmv': 0.0, 'adjust_gmv': 0.0, 'true_orders': 0, 'predict_orders': 0, 'adjust_orders': 0}], '1234561234564': [{'audo_id': 104, 'insert_time': datetime.datetime(2020, 2, 29, 17, 43, 12), 'update_time': datetime.datetime(2020, 2, 29, 17, 43, 12), 'status': 1, 'cid': '123456', 'shike': '2020-02-27 10:00', 'goods_bid': '1234561234564', 'did': 1, 'price': 12.5, 'true_single_sale': 100, 'predict_single_sale': 0, 'adjust_single_sale': 0, 'true_gmv': 125.5, 'predict_gmv': 0.0, 'adjust_gmv': 0.0, 'true_orders': 0, 'predict_orders': 0, 'adjust_orders': 0}, {'audo_id': 106, 'insert_time': datetime.datetime(2020, 2, 29, 17, 43, 13), 'update_time': datetime.datetime(2020, 2, 29, 17, 43, 13), 'status': 1, 'cid': '123456', 'shike': '2020-02-27 10:15', 'goods_bid': '1234561234564', 'did': 1, 'price': 24.0, 'true_single_sale': 10, 'predict_single_sale': 0, 'adjust_single_sale': 0, 'true_gmv': 1250.0, 'predict_gmv': 0.0, 'adjust_gmv': 0.0, 'true_orders': 0, 'predict_orders': 0, 'adjust_orders': 0}]}"
    #
    # print(json.dumps(jsonD))

    # time = ['09:00:01', '09:25:00', '09:37:05', '09:45:00', '09:45:01', '09:59']
    # for t in time:
    #     hourAndMinute = DateUtils.get_new_time_15_minute(t)
    #     if hourAndMinute == None:
    #         print('日期格式不正确')
    #         continue
    #     print(hourAndMinute[0], hourAndMinute[1])
    # day: str = '2020-02-26'
    # daysStart = datetime.strptime(day + ' 00:00',"%Y-%m-%d %H:%M")
    #
    # dayEnd = datetime.strptime("2020-02-27" + ' 00:00', "%Y-%m-%d %H:%M")
    #
    #
    # lisg = [{"shike": "2020-02-26 09:15", "goods_bid":"123456dksh"}, {"shike": "2020-02-26 09:00", "goods_bid":"123456dksh"}, {"shike": "2020-02-26 09:30", "goods_bid":"123456dksh"},{"shike": "2020-02-26 08:00", "goods_bid":"123456dksh"}]
    # lisg.sort(key = lambda x:x["shike"])
    #
    # date = datetime.strptime("2020-02-26 00:00", "%Y-%m-%d %H:%M")
    #
    # map = {}
    # for item in lisg:
    #     map[item["shike"]] = item
    #
    # while dayEnd > date:
    #
    #     key = date.strftime("%Y-%m-%d %H:%M")
    #     value = map.get('2020-02-26 09:15', default=None)
    #
    #     if value == None:
    #         print("没有")
    #
    #     date = date + timedelta(minutes=15)
