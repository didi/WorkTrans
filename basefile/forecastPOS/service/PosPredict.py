from forecastPOS.service.posDBService import PosDBService
import datetime
import numpy as np
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog, tracebackLog
from config.pos_auto_conf import PosAutoConfig
import threading
import pandas as pd
import time
from forecastPOS.algorithm.lstm import LstmForecast
from forecastPOS.algorithm.prophet import ProphetForecast
from forecastPOS.algorithm.seq2seq import seq2seqForecast
from forecastPOS.algorithm.dnn_factory import ClassFactory
from forecastPOS.algorithm.dnn_factory import DeepModel
class PosPredict():
    def __init__(self):
        self.model_factory = ClassFactory.subclasses_dict(DeepModel)

    def get_data(self,did, startdate, enddate, preType, cid):
        data = PosDBService.getHistoryPosData(did, startdate, enddate, preType, cid)
        return data

    def predict_Prophet(self,cid,did,startPreDay,endPreDay,preType):
        message={"res_type":0,"startPreDay":startPreDay,"endPreDay":endPreDay}
        Prophet_ = ProphetForecast(cid,did,preType)
        res = Prophet_.process(message)
        return res

    def predict_dnn(self,cid,did,startPreDay,endPreDay,preType,data,model_conf,model_name):
        req_days = model_conf[model_name]["req_days"]
        pred_type = model_conf[model_name]["pred_type"]
        starPosday = DateUtils.nDatesAgo(startPreDay,req_days)
        date_series = pd.date_range(start=starPosday, end=startPreDay, freq=pred_type).tolist()[:-1]
        date_series = [tt.strftime("%Y-%m-%d %H:%M") for tt in date_series]
        data_ = [data.get(tt,0) for tt in date_series]
        model = self.model_factory[model_name]
        model_instance = model(cid,did,preType)
        message = {"startPreDay":startPreDay, "endPreDay":endPreDay,"data":data_}
        res = model_instance.process(message)
        return res

    def predict_avg_and_smooth(self,cid,did,startPreDay,endPreDay,preType,predictParam):
        cycleLenth = predictParam.get('dayCount', 7)
        endPreDay = DateUtils.nDatesAgo(endPreDay,-1)
        did_req = did
        infoLog.info("请求的did是: %s ,参照的did: %s" % (str(did), str(did_req)))
        # 获取灵活的模型参数
        coffDict = PosAutoConfig.config_coffDict
        # cycles, smoothCoef = coffDict.get('%s_deepDict_%d' % (preType.lower(), did), [30, 1])
        cycles = 100
        smoothCoef = predictParam.get('smoothCoef', 0.9)
        avgCycles = cycles
        # cyclesCoef = [0 for _ in range(cycles)]
        cyclesCoef = predictParam.get('cyclesCoef', np.zeros((1, cycles))[0].tolist())
        deepCycles = coffDict.get('%s_deepDict_%d' % (preType.lower(), did), [30, 1])[0]
        # startBaseDay = DateUtils.nDatesAgo(startPreDay, avgCycles * cycleLenth)
        startBaseDay = DateUtils.nDatesAgo(startPreDay, max([avgCycles, deepCycles]) * cycleLenth)
        historyPosData = self.get_data(did, startBaseDay, startPreDay, preType, cid)
        iswoqu = True     #false->true
        s = time.time()
        avgDict = PosDBService.extendPreday('avgm', did_req, startPreDay, preType, cycleLenth, cycles, cyclesCoef,
                                            endPreDay, smoothCoef, iswoqu, cid, historyPosData)
        smoothDict = PosDBService.extendPreday('smooth', did_req, startPreDay, preType, cycleLenth, cycles, cyclesCoef,
                                               endPreDay, smoothCoef, iswoqu, cid, historyPosData)
        iswoqu = False
        cycles, smoothCoef = coffDict.get('%s_deepDict_%d' % (preType.lower(), did), [30, 1])
        if str(cid) == '50000671':  # 沃尔玛
            cycles = 2
        elif str(cid) == '50000735' and str(did) == '12':  # 喜茶 12
            cycles = 17
        elif str(cid) == '50000735' and str(did) == '22':  # 喜茶 22
            cycles = 16
        deepDict = PosDBService.extendPreday('avgm', did_req, startPreDay, preType, cycleLenth, cycles,
                                             cyclesCoef, endPreDay, smoothCoef, iswoqu, cid, historyPosData)

        return avgDict, smoothDict, deepDict

    def process(self, predictParam):
        cid = predictParam['cid']
        did = predictParam['did']
        startPreDay = predictParam['startDay']
        endPreDay = predictParam['endDay']
        preType = predictParam.get('preType', 'truePeoples')
        avg,smooth,deep = self.predict_avg_and_smooth(cid, did, startPreDay, endPreDay, preType,predictParam)
        model_conf = PosAutoConfig.model_conf
        endPreDay = DateUtils.nDatesAgo(endPreDay, -1)  # 往后延长一天，但是不包含零点
        prophetDict = self.predict_Prophet(cid, did, startPreDay, endPreDay, preType)
        if not prophetDict:
            prophetDict = avg
        cycleLenth = max([info['req_days'] for k,info in model_conf.items()]) #获取深度模型需要的预测前最长的天数
        startPosday = DateUtils.nDatesAgo(startPreDay,cycleLenth)
        predict_data = self.get_data(did,startPosday,startPreDay,preType,cid)
        lstmDict = self.predict_dnn(cid,did, startPreDay, endPreDay,preType,predict_data,model_conf,"lstm")
        seq2seqDict = self.predict_dnn(cid,did,startPreDay, endPreDay,preType,predict_data,model_conf,"seq2seq")
        if not lstmDict:
            lstmDict=deep
        if not seq2seqDict:
            seq2seqDict=deep
        predictData = {
            'avgDict': PosDBService.tuncDict(avg),
            'smoothDict': PosDBService.tuncDict(smooth),
            'deepDict': PosDBService.tuncDict(lstmDict),
            'prophetDict': PosDBService.tuncDict(prophetDict),
            'seq2seqDict': PosDBService.tuncDict(seq2seqDict)
        }
        PosDBService.savePredict(preType,predictData['deepDict'],cid,did)
        return predictData

if __name__ == '__main__':
    data = {"preType":"trueGMV","startDay":"2019-11-01","predictType":"CUSTOM","endDay":"2019-11-03","did":4954,"cid":50000031}
    pos = PosPredict()
    result = pos.process(data)
    print( result)