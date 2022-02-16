import json
from utils.mysql_factory import Pos_base_Mysql_Query,Pos_view_Mysql_Query,Pos_task_detail_Query,Push_task_status_Query
from utils.myLogger import infoLog, tracebackLog
import datetime
from utils.global_keys  import *
from collections import namedtuple
import time
pos_detail = namedtuple('pos',["cid","did","gmt_bill","money","data_value","peoples","order_no"])
class PosDB_process():
    def __init__(self,dbpool):
        self.dbpool = dbpool

    def check_headers(self,raw_data):
        headers = {}
        cid = raw_data.get('cid', None)
        did = raw_data.get('did', None)
        batchId = raw_data.get('batchId', None)
        serialNumber = raw_data.get('serialNumber', None)
        totalCount = raw_data.get('totalCount', None)
        requestCount = raw_data.get('requestCount', None)
        startTime = raw_data.get('startTime', None)
        endTime = raw_data.get('endTime', None)
        data_len = len(raw_data.get('data',[]))
        if not did or not cid or not batchId or not serialNumber or not totalCount or not requestCount or not startTime or not endTime or data_len==0:
            tracebackLog.error('data_miss_error:'
                               'did:{}|'
                               'cid:{}|'
                               'batchId:{}|'
                               'serialNumber:{}|'
                               'totalCount:{}|'
                               'requestCount:{}|'
                               'startTime:{}|'
                               'endTime:{}|data_num:{}'.
                               format(did,cid, batchId, serialNumber, totalCount, requestCount, startTime, startTime,data_len))
            return True,headers
        headers={"did":did,"cid":cid,"batchId":batchId,
                 "serialNumber":serialNumber,
                 "totalCount":totalCount,"requestCount":requestCount,
                 "startTime":startTime,"endTime":endTime,"data_count":data_len}
        return False,headers

    def pos_data_format(self,raw_data):
        res_items = []
        datas = raw_data['data']
        cid = raw_data['cid']
        did = raw_data['did']
        start_time = "2100-01-01 00:00:00"
        end_time = "2000-01-01 00:00:00"
        updateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for da in datas:
            try:
                orderNo = da.get('orderNo', None)
                if not orderNo:
                    continue

                gmtBill = da.get('gmtBill', '')
                if gmtBill:
                    start_time = gmtBill if gmtBill< start_time else start_time
                    end_time = gmtBill if gmtBill>end_time else end_time
                gmtTurnover = da.get('gmtTurnover', '0')
                money = float(da.get('money', 0))

                data_value = int(float(da.get('money', 0))) * 100
                transaction_num = int(da.get('transactionNum', 0))
                peoples = int(da.get('peoples', 0))

                singleSales = int(da.get('singleSales', '0'))
                commodity_code = da.get('commodityCode', '0')
                payment = da.get('payment', '0')
                deviceCode = da.get('deviceCode', '0')
                pre_data = (cid, did, gmtBill,
                            gmtTurnover, money,
                            data_value, transaction_num,
                            peoples,singleSales,
                            commodity_code, payment,
                            deviceCode, orderNo,
                            updateTime, updateTime, 1,
                          )
                res_items.append(pre_data)
            except Exception as e:
                tracebackLog.error(e)
                tracebackLog.error('traceid:{}_{} process_data_error:{}'.format(raw_data["batchId"],raw_data['serialNumber'],da))
        infoLog.info("traceid:{}_{} origin_data:{} after_data:{}".format(raw_data["batchId"],
                                                                         raw_data['serialNumber'],
                                                                         len(datas),len(res_items)))
        start_time = updateTime if start_time > updateTime else start_time
        end_time = updateTime if end_time=="2000-01-01 00:00:00" else end_time
        return res_items,start_time,end_time

    def insert_pos_data(self,items):
        sql = Pos_base_Mysql_Query.inert_pos_data()
        ids = self.dbpool.update_sql_many(sql,items)
        return ids

    def _check_push_detail(self,headers):
        push_token = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        headers["pushToken"] = push_token
        sql = Pos_task_detail_Query.insert_sql()
        item =(headers["batchId"],headers["serialNumber"],
               headers["totalCount"],headers["requestCount"],
               headers["startTime"],headers["endTime"],
               push_token,push_token,headers["cid"],headers["did"])
        sql=sql%item
        st = time.time()
        ids  = self.dbpool.update_sql_one(sql)
        infoLog.info("traceid:{}_{} update_push_status_time_cost:{}".format( headers['batchId'],headers['serialNumber'],time.time()-st))
        if ids ==-1:
            infoLog.info('traceid:{}_{} data_has_processed'.format(
                          headers['batchId'],headers['serialNumber']))
            return True 
        return False

    def update_push_status(self,headers):
        view_proc_state = 0
        modify_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        item = (headers['batchId'],headers["data_count"],
                view_proc_state,headers["totalCount"],modify_time,headers["cid"],headers["did"])
        sql1 = Push_task_status_Query.update_status_Query()
        sql1 = sql1%item
        st = time.time()
        ids= self.dbpool.update_sql_one(sql1)
        infoLog.info("traceid:{}_{} update_push_status0_time_cost:{}".format(headers['batchId'],headers['serialNumber'],time.time()-st))
        if ids==-1:
            return False
        '''
        轮寻策略暂时不做，每次数据都需要更新view
        sql2 = Push_task_status_Query.get_received_count()
        sql2 =  sql2%(headers['batch_id'])
        res = self.dbpool.get_sql_one(sql2)
        if res[0]==headers["totalCount"]:
             return True
        '''
        return True
    def update_view_pos(self,headers):
        batch_id = headers["batchId"]
        serialNumber = headers["serialNumber"]
        start_time =  headers['startTime']
        end_time = headers['endTime']
        cid = headers['cid']
        did = headers['did']
        get_sql = Pos_base_Mysql_Query._get_info_data()
        get_sql = get_sql%(start_time,end_time,cid,did)
        data = self.dbpool.get_sql_all(get_sql)
        info_dict={}
        # cid,did,gmt_bill,money,data_value,peoples,order_no
        for da in data: #2020-01-01 10:
            p = pos_detail(*da)
            gmt_bill =str(p.gmt_bill)
            mode = str(15*(int(gmt_bill[14:16])//15))
            mode = '00' if mode=='0' else mode
            shike = gmt_bill[:14]+mode
            info = info_dict.get(shike,{})
            info['truePeoples'] = info.get('truePeoples',0)+int(p.peoples)
            info['trueGMV'] = info.get('trueGMV',0)+float(p.data_value)/100
            info['trueOrders'] = info.get('trueOrders',0)+1
            info_dict[shike]=info
        items=[]
        predictGMV,adjustGMV,predictPeoples,adjustPeoples,status,predictOrders,adjustOrders=0,0,0,0,0,0,1
        insertTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for k,v in info_dict.items():
            item = (cid,did,k,v['trueGMV'],predictGMV,adjustGMV,
                    v["truePeoples"],predictPeoples,adjustPeoples,
                    status,insertTime,insertTime,v["trueOrders"],
                    predictOrders,adjustOrders)
            items.append(item)
        if len(items)==0:
            tracebackLog.error('data is none cid:{},did:{},start_time:{},end_time:{}'.format(cid,did,start_time,end_time))
        else:
            st = time.time()
            sql = Pos_view_Mysql_Query.update_view_pos()
            ids=self.dbpool.update_sql_many(sql,items)
            infoLog.info("traceid:{}_{} update_view_post_time_cost:{}".format(batch_id,serialNumber,time.time()-st))
            if ids ==-1:
               return RES_102
            st = time.time()
            ids = self.dbpool.update_sql_one(Push_task_status_Query.update_Push_task_status()%(insertTime,batch_id))
            infoLog.info("traceid:{}_{} update_push_status1_post_time_cost:{}".format(batch_id, serialNumber, time.time() - st))
            if ids ==-1:
               return RES_102
        return RES_100

    def process(self,raw_data):
        flag,headers = self.check_headers(raw_data)
        if flag:
            return RES_401
        is_push = self._check_push_detail(headers)
        # 为了解决上线导致没有处理完数据，后面woqu方可以启动重试机制
        # if is_push:
        #    return RES_100
        data_items, start_time, end_time = self.pos_data_format(raw_data)
        headers["startTime"] = start_time
        headers["endTime"] = end_time
        if len(data_items) == 0:
            return RES_400
        st=time.time()
        ids = self.insert_pos_data(data_items)
        infoLog.info("traceid:{}_{} inert_into_pos_time_cost:{}".format( headers['batchId'],headers['serialNumber'],time.time()-st))
        if not ids:
            return RES_400
        is_view = self.update_push_status(headers)
        if not is_view:
            return RES_400
        res = self.update_view_pos(headers)
        return res

        '''
         if is_view:
           res=self.update_view_pos(headers)
           return res
        return RES_100
        '''





