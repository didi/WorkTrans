"""
@author: shenzh
@contact: shenzihan_i@didichuxing.com
@file: empCertService.py
@time: 2019-10-09 14:48
@desc:
"""
from datetime import datetime
from typing import Dict
from utils.myLogger import infoLog
from POC.model.empCertDB import empCertDB
from tornado import gen


class empCertService:

    @staticmethod
    @gen.coroutine
    def doRequest(raw_data:Dict):

        save_result = {'code': 0, 'result': '未处理'}
        cid = raw_data['cid']
        for entity in raw_data['skillData']:
            eid = entity['eid']
            opt = entity['opt']
            # for entity1 in entity['certs']:
            #     certname = entity1['certname']
            #     closingdate = entity1['closingdate']
            # modify操作
            if opt == 'update':
                res = empCertService.Emp_cart_modify(cid, eid, entity)
                if res:
                    save_result = {'code': 100, 'result': '操作成功'}
                else:
                    save_result = {'code': 101, 'result': 'DB操作失败'}
                    break
        raise gen.Return(save_result)

    @staticmethod
    def Emp_cart_delete(cid:str,eid:str):
        '''
        软删除
        :param cid:
        :param eid:
        :return:
        '''
        res_flag = True
        log_time1 = datetime.now()
        res_flag = empCertDB.delete_record(cid, eid)
        log_time2 = datetime.now()
        infoLog.info('外层删除耗时: ' + str(log_time2 - log_time1))
        return res_flag

    @staticmethod
    def Emp_cart_modify(cid:str, eid:str, entity:Dict):
        '''
        修改操作
        :param cid:
        :param eid:
        :param entity:
        :return:
        '''
        res_flag = True
        opt = entity['opt']
        for certs in entity['certs']:
            certname = certs['certname']
            closingdate = certs['closingdate']

            res_flag = empCertDB.update_record(cid,eid,opt,certname,closingdate)
        return res_flag

if __name__ == '__main__':
    data = {"token": "d0055e4e2dd73c1848a54f4591d1da43", "timestr": "2019-10-11 16:26:24.932219","cid":"123456","skillData":[{"eid":"10","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"88","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-14"}]},{"eid":"141","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-17"}]},{"eid":"244","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-12"}]},{"eid":"256","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"369","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-18"}]},{"eid":"472","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"633","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"677","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"680","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-07-16"}]},{"eid":"730","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"732","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]},{"eid":"791","opt":"update","certs":[{"certname":"健康证","closingdate":"2019-08-10"}]}]}

    res = empCertService.doRequest(data)
    print(res)

