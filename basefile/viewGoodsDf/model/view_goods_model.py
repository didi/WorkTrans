#!/usr/bin/env python
# encoding: utf-8

"""
@author: sean
@file: base_goods_task.py
@time: 2020/02/26 13:18
@desc: 预测每15 分钟预测量详细表
"""
import datetime

from specialEvent.model.special_event_scope_model import SpecialEventScopeModel
from utils.testDBPool import DBPOOL
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
import pymysql


class ViewGoodsModel:

    @classmethod
    def insertObj(cls, viewGoodsModel) -> bool:
        if viewGoodsModel is None or len(viewGoodsModel) < 1:
            return False
        cid = viewGoodsModel.get("cid", None)
        did = viewGoodsModel.get("did", None)
        shike = viewGoodsModel.get("shike", None)
        goodsBid = viewGoodsModel.get("goods_bid", None)
        price = viewGoodsModel.get("price", None)
        trueSingleSale = viewGoodsModel.get("trueSingleSale", None)
        predictSingleSale = viewGoodsModel.get("predictSingleSale", None)
        adjustSingleSale = viewGoodsModel.get("adjustSingleSale", None)
        trueGMV = viewGoodsModel.get("trueGMV", None)
        predictGMV = viewGoodsModel.get("predictGMV", None)
        adjustGMV = viewGoodsModel.get("adjustGMV", None)
        trueOrders = viewGoodsModel.get("trueOrders", None)
        predictOrders = viewGoodsModel.get("predictOrders", None)
        adjustOrders = viewGoodsModel.get("adjustOrders", None)
        truePeoples = viewGoodsModel.get("truePeoples", None)
        predictPeoples = viewGoodsModel.get("predictPeoples", None)
        adjustPeoples = viewGoodsModel.get("adjustPeoples", None)
        return ViewGoodsModel.insert(cid, goodsBid, shike, did, 1, price, trueSingleSale, predictSingleSale,
                                     adjustSingleSale,
                                     trueGMV, predictGMV, adjustGMV, trueOrders, predictOrders, adjustOrders,
                                     truePeoples, predictPeoples, adjustPeoples)

    @classmethod
    def insert(cls, cid: str, goods_bid: str, shike: str, did: int, status: int, price: int, trueSingleSale: int,
               predictSingleSale: int,
               adjustSingleSale, trueGMV, predictGMV, adjustGMV, trueOrders, predictOrders, adjustOrders,
               truePeoples, predictPeoples, adjustPeoples) -> bool:

        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        res_flag = True
        allsql = 'INSERT INTO view_goods_df (cid, shike, goods_bid, did, true_single_sale, predict_single_sale, ' \
                 'adjust_single_sale, true_gmv, predict_gmv, adjust_gmv, true_orders, predict_orders, adjust_orders,' \
                 'true_Peoples,predict_Peoples,adjust_Peoples ,price, insert_time, update_time, status)  VALUES ("{}",' \
                 '"{}","{}",{},{},{},{},{},{},{},{},{},{},{},{},{},{},"{}","{}",{});'.format(
            cid, shike, goods_bid, did, trueSingleSale, predictSingleSale, adjustSingleSale, trueGMV, predictGMV,
            adjustGMV, trueOrders, predictOrders, adjustOrders, truePeoples, predictPeoples, adjustPeoples, price,
            now_datetime, now_datetime, status)
        with conn.cursor() as cursor:
            sql = allsql
            try:
                cursor.execute(sql)
                conn.commit()
                infoLog.debug('success, sql: ' + allsql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allsql)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def updateObj(cls, viewGoodsModel) -> bool:
        if viewGoodsModel is None or len(viewGoodsModel) < 1:
            return False
        cid = viewGoodsModel.get("cid", None)
        did = viewGoodsModel.get("did", None)
        shike = viewGoodsModel.get("shike", None)
        goodsBid = viewGoodsModel.get("goods_bid", None)
        trueSingleSale = viewGoodsModel.get("trueSingleSale", None)
        predictSingleSale = viewGoodsModel.get("predictSingleSale", None)
        adjustSingleSale = viewGoodsModel.get("adjustSingleSale", None)
        trueGMV = viewGoodsModel.get("trueGMV", None)
        predictGMV = viewGoodsModel.get("predictGMV", None)
        adjustGMV = viewGoodsModel.get("adjustGMV", None)
        trueOrders = viewGoodsModel.get("trueOrders", None)
        predictOrders = viewGoodsModel.get("predictOrders", None)
        adjustOrders = viewGoodsModel.get("adjustOrders", None)
        truePeoples = viewGoodsModel.get("truePeoples", None)
        predictPeoples = viewGoodsModel.get("predictPeoples", None)
        adjustPeoples = viewGoodsModel.get("adjustPeoples", None)
        return ViewGoodsModel.update(cid, goodsBid, shike, did, trueSingleSale, predictSingleSale, adjustSingleSale,
                                     trueGMV, predictGMV, adjustGMV, trueOrders, predictOrders, adjustOrders,
                                     truePeoples, predictPeoples, adjustPeoples)

    @classmethod
    def update(cls, cid: str, goods_bid: str, shike: str, did: int, trueSingleSale: int,
               predictSingleSale: int,
               adjustSingleSale, trueGMV, predictGMV, adjustGMV, trueOrders, predictOrders, adjustOrders,
               truePeoples, predictPeoples, adjustPeoples) -> bool:

        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        res_flag = True

        _set = ''
        where = "cid = '{}' and did = '{}' and goods_bid = '{}' and shike = '{}'".format(cid, did, goods_bid, shike)
        temp = []
        if trueSingleSale is not None:
            temp.append('true_single_sale = ' + str(trueSingleSale))
        if predictSingleSale is not None:
            temp.append('predict_single_sale = ' + str(predictSingleSale))
        if adjustSingleSale is not None:
            temp.append('adjust_single_sale = ' + str(adjustSingleSale))
        if trueGMV is not None:
            temp.append('true_gmv = ' + str(trueGMV))
        if predictGMV is not None:
            temp.append('predict_gmv = ' + str(predictGMV))
        if adjustGMV is not None:
            temp.append('adjust_gmv = ' + str(adjustGMV))

        if trueGMV is not None:
            temp.append('true_orders = ' + str(trueOrders))
        if predictGMV is not None:
            temp.append('predict_orders = ' + str(predictOrders))
        if adjustGMV is not None:
            temp.append('adjust_orders = ' + str(adjustOrders))

        if trueGMV is not None:
            temp.append('true_Peoples = ' + str(truePeoples))
        if predictGMV is not None:
            temp.append('predict_Peoples = ' + str(predictPeoples))
        if adjustGMV is not None:
            temp.append('adjust_Peoples = ' + str(adjustPeoples))

        if len(temp) > 0:
            _set = ",".join(map(str, temp))
        print(_set)
        if len(_set) < 1 or len(where) < 1:
            return False

        _set += ", update_time = '{}'".format(now_datetime)

        allsql = 'UPDATE view_goods_df SET {} where {}'.format(_set, where)
        print(allsql)
        with conn.cursor() as cursor:
            sql = allsql
            try:
                cursor.execute(sql)
                conn.commit()
                infoLog.debug('success, sql: ' + allsql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allsql)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def delete(cls, cid: str, goods_bid: str) -> bool:
        if len(cid) < 1 or len(goods_bid) < 1:
            return False
        conn = DBPOOL.connection()
        res_flag = True
        allSql = 'DELETE FROM view_goods_df WHERE cid=%s and goods_bid = %s;'.format(cid, goods_bid)
        with conn.cursor() as cursor:
            sql = """
                   DELETE FROM view_goods_df WHERE cid=%s and goods_bid = %s;
                  """
            try:
                cursor.execute(sql, (cid, goods_bid))
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allSql)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def list(cls, cid: str, did: int, goods_bid: str, shike: str):
        if len(cid) < 1 or did is None or len(shike) < 1:
            return None

        conn = DBPOOL.connection()

        allSql = "select * from view_goods_df where cid = {} and goods_bid = {} and did = {} and shike like '%{}%' " \
                 "and status = 1 order by shike ".format(cid, goods_bid, did, shike)
        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                print(allSql)
                infoLog.debug(
                    "FAILED, sql: " + allSql)
                return None
        conn.close()
        return result

    @classmethod
    def listByShike(cls, cid: str, did: int, goods_bid: str, start: str, end: str, page: int, size: int):
        if len(cid) < 1 or did is None or len(start) < 1 or len(end) < 1:
            return None
        hasPage = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            hasPage = True
        conn = DBPOOL.connection()

        startShike = cls.getShike(start, True)
        endShike = cls.getShike(end, False)
        # FIXME: 这里应该返回一个对象， 暂时还不清楚怎么返回，有没有通用得返回，暂定
        # 防止查询数据量过大，日期必填 最多查询一个月得

        if startShike is None or endShike is None:
            return None
        if cls.diffStartEndDay(startShike, endShike) > 31:
            return None

        where = 'cid = "{}" and did = {}'.format(cid, did)

        if goods_bid is not None:
            where = where + (" and goods_bid = '{}'".format(goods_bid))

        where = where + (" and shike >= '{}' and shike < '{}'".format(startShike, endShike))
        countSql = "select count(*) from view_goods_df where status = 1 and {}".format(
            where)
        print(countSql)
        where = where + (" order by shike")
        if hasPage:
            # page 重0 开始
            limitStart = page * size
            limitEnd = size
            where = where + (" limit {},{}".format(limitStart, limitEnd))

        allSql = "select cid, shike, goods_bid, did, price, true_single_sale, predict_single_sale ," \
                 "adjust_single_sale,true_gmv ,predict_gmv ,adjust_gmv ,true_orders ,predict_orders ,adjust_orders, " \
                 "true_peoples ,predict_peoples ,adjust_peoples from view_goods_df where status = 1 and {}".format(
            where)
        count = 0
        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                if hasPage:
                    cursor.execute(countSql)
                    count = cursor.fetchall()[0]["count(*)"]
                    conn.commit()
                else:
                    count = None
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                print(allSql)
                infoLog.debug(
                    "FAILED, sql: " + allSql)
                return None
        conn.close()
        print(count)
        return {"data":result, "count": count}

    @classmethod
    def listByShikes(cls, cid: str, did: int, goods_bid: str, shikes, page: int, size: int):
        if len(cid) < 1 or did is None or len(shikes) < 1:
            return None

        hasPage = False
        if (page is not None and page > -1) and (size is not None and size > 0):
            hasPage = True

        conn = DBPOOL.connection()

        # FIXME: 这里应该返回一个对象， 暂时还不清楚怎么返回，有没有通用得返回，暂定
        # 防止查询数据量过大，shikes 日期必填 最多查询一个月得

        where = 'cid = {} and did = {}'.format(cid, did)

        if goods_bid is not None:
            where = where + (" and goods_bid = '{}'".format(goods_bid))

        where = where + (" and shike in {}".format(tuple(shikes)))
        countSql = "select count(*) from view_goods_df  where status = 1 and {}".format(
            where)
        print(countSql)
        where = where + (" order by shike")
        if hasPage:
            # page 重0 开始
            limitStart = page * size
            limitEnd = size
            where = where + (" limit {},{}".format(limitStart, limitEnd))
        allSql = "select cid, shike, goods_bid, did, price, true_single_sale, predict_single_sale ," \
                 "adjust_single_sale,true_gmv ,predict_gmv ,adjust_gmv ,true_orders ,predict_orders ,adjust_orders, " \
                 "true_peoples ,predict_peoples ,adjust_peoples from view_goods_df where status = 1 and {}".format(
            where)

        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                if hasPage:
                    cursor.execute(countSql)
                    count = cursor.fetchall()[0]["count(*)"]
                    conn.commit()
                else:
                    count = None
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                print(allSql)
                infoLog.debug(
                    "FAILED, sql: " + allSql)
                return None
        conn.close()
        return {"data":result, "count": count}

    @classmethod
    def getCid(cls):
        conn = DBPOOL.connection()
        allSql = 'SELECT DISTINCT cid FROM view_goods_df'

        result = []

        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allSql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def getDids(cls, cid):
        # 容错
        if cid is None or len(cid) < 1:
            return []

        conn = DBPOOL.connection()
        allSql = 'SELECT DISTINCT did FROM view_goods_df where cid = {}'.format(cid)

        result = []

        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allSql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def getBids(cls, cid, did):
        # 容错
        if cid is None or len(cid) < 1 or did is None or did < 1:
            return []

        conn = DBPOOL.connection()
        allSql = 'SELECT DISTINCT goods_bid FROM view_goods_df where cid = {} and did = {}'.format(cid, did)

        result = []

        with conn.cursor() as cursor:
            sql = allSql
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                conn.commit()
                infoLog.debug('success, sql: ' + allSql)
            except Exception as e:
                infoLog.warning(
                    "FAILED, sql: " + allSql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def getShike(cls, data: str, isStart: bool):
        try:
            # 如果是 %Y-%m-%d %H:%M 直接查询， 如果不是 开始 增加  00：00， 结束 增加 23：00
            datetime.datetime.strptime(data, '%Y-%m-%d %H:%M')
            return data
        except ValueError:
            try:
                datetime.datetime.strptime(data, '%Y-%m-%d')
                data = data + (" 00:00" if isStart else " 23:59")
                return data
            except ValueError:
                return None

    @classmethod
    def diffStartEndDay(cls, start, end):

        try:
            start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M")
            end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M")
        except ValueError:
            return 1000
        return (end - start).days

    @classmethod
    def getBasePosByEvents(cls, did, start_base_day, start_pre_day, pre_type, cid):
        """
        获取(特殊事件)影响的参考的POS历史数据
        :param:did 部门id
        :param:start_base_day 预测参考的数据的历史数据开始时间，比如使用历史数据为（20190101）-20191001，预测20191002-20191007，则此处为20190101
        :param:start_pre_day 预测开始时间，比如使用历史数据为20190101-20191001，预测（20191002）-20191007，则此处为20191002
        :param:pre_type 预测类型 包含：trueGMV：GMV预测；truePeoples：客流量预测；trueOrders:订单量预测；
        :param:cid 部门cid
        :return:字典对象：history_data_dict；key:15分钟时间(e.g.:'2020-03-02 10:00')；value:此时刻对应的POS量比如（e.g.:（GMV）2301.5元）
        """
        return ViewGoodsModel.getBasePos(did, cid, start_base_day, start_pre_day, pre_type, 'include')

    @classmethod
    def getBasePosByNoEvents(cls, did, start_base_day, start_pre_day, pre_type, cid):
        """
        获取(剔除特殊事件)影响的参考的POS历史数据
        :param:did 部门id
        :param:start_base_day 预测参考的数据的历史数据开始时间，比如使用历史数据为（20190101）-20191001，预测20191002-20191007，则此处为20190101
        :param:start_pre_day 预测开始时间，比如使用历史数据为20190101-20191001，预测（20191002）-20191007，则此处为20191002
        :param:pre_type 预测类型包含：trueGMV：GMV预测；truePeoples：客流量预测；trueOrders:订单量预测；
        :param:cid 部门cid
        :return:字典对象：history_data_dict；key:15分钟时间(e.g.:'2020030210:00')；value:此时刻对应的POS量比如（e.g.:（GMV）2301.5元）
        """

        return ViewGoodsModel.getBasePos(did, cid, start_base_day, start_pre_day, pre_type, 'exclude')

    @classmethod
    def getBasePos(cls, did, cid, start_base_day, start_pre_day, pre_type, special_event_type):
        """
        获取POS历史数据
        :param:did 部门id
        :param:cid
        :param:start_base_day 预测参考的数据的历史数据开始时间，比如使用历史数据为（20190101）-20191001，预测20191002-20191007，则此处为20190101
        :param:start_pre_day 预测开始时间，比如使用历史数据为20190101-20191001，预测（20191002）-20191007，则此处为20191002
        :param:pre_type 预测类型 包含：trueGMV：GMV预测；truePeoples：客流量预测；trueOrders:订单量预测；
        :param:special_event_type 特殊事件类型 包含 include:仅含特殊事件影响的; exclude:仅含无特殊事件影响的； all：全部
        :return:字典对象：history_data_dict；key:15分钟时间(e.g.:'2020-03-02 10:00')；value:此时刻对应的POS量比如（e.g.:（GMV）2301.5元）
        """

        history_data_dict = {}
        start_time = start_base_day + ' 00:00'
        end_time = start_pre_day + ' 00:00'
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
                    SELECT
                        g.cid,
                        g.did,
                        g.shike,
                        g.goods_bid,
                        g.price,
                        g.true_gmv,
                        g.true_orders,
                        g.true_peoples
                    FROM
                        view_goods_df g
                    WHERE
                        g.STATUS = 1
                        AND g.shike>=%s
                        AND g.shike<%s
                        AND g.did = %s
                        AND g.cid = %s
                    """
            try:
                result_index = 5
                if pre_type == 'trueGMV':
                    result_index = 5
                elif pre_type == 'truePeoples':
                    result_index = 7
                elif pre_type == 'trueOrders':
                    result_index = 6
                cursor.execute(sql, (start_time, end_time, did, cid))
                results = cursor.fetchall()

                if special_event_type == 'include':  # 只考虑包含特殊事件的
                    goods_ids = SpecialEventScopeModel.get_goods_ids(cid, did, start_time, end_time)
                    for one in results:
                        if str(one[3]) in goods_ids:
                            history_data_dict[one[2]] = one[result_index]

                elif special_event_type == 'exclude':  # 只考虑排除特殊事件的
                    goods_ids = SpecialEventScopeModel.get_goods_ids(cid, did, start_time, end_time)
                    for one in results:
                        if str(one[3]) not in goods_ids:
                            history_data_dict[one[2]] = one[result_index]

                else:  # 不考虑特殊事件 全取出
                    for one in results:
                        history_data_dict[one[2]] = one[result_index]
            except Exception:
                conn.rollback()
        conn.close()
        return history_data_dict


if __name__ == '__main__':
    r = ViewGoodsModel.getBasePosByNoEvents('11', '2020-02-27', '2020-02-28', 'trueGMV', '123456')
    print(r)
