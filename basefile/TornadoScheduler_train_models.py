from datetime import datetime,timedelta
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import RequestHandler, Application
from apscheduler.schedulers.tornado import TornadoScheduler
from utils.testDBPool import DBPOOL
from utils.myLogger import infoLog
import numpy as np
import pandas as pd
import sys

from forecastPOS.algorithm.lstm import DeepModel
from forecastPOS.algorithm.prophet import ProphetForecast
from forecastPOS.algorithm.seq2seq import seq2seqForecast
import argparse
from forecastPOS.algorithm.dnn_factory import ClassFactory
from config.pos_auto_conf import PosAutoConfig
from sklearn.metrics import mean_squared_error

#从数据库读取历史数据
def getBasePos(cid, did,now_date, history):
    """
    获取预测的参考的历史数据
    :param : did 部门id
    :param : startBaseDay 预测参考的数据的历史数据开始时间
    :param : startPreDay 预测开始时间
    :return:
    """

    newSql = """
            select cid,did,shike,truepeoples,trueorders,truegmv from view_pos_info_df
            where shike>=%s and shike<%s and cid = %s and did = %s and status = 0                
            """

    conn = DBPOOL.connection()
    cursor = conn.cursor()
    historydata = pd.DataFrame()

    try:
        cursor.execute(newSql, (now_date - timedelta(days=history), now_date,cid,did))
        alldata = cursor.fetchall()
        historydata = pd.DataFrame(alldata,columns=['cid','did','shike','truepeoples','trueorders','truegmv'])
        conn.commit()
    except Exception:
        infoLog.warning('FAILED, sql: select cid,did,shike,truepeoples,trueorders,truegmv from view_pos_info_df where shike>=%s and shike<%s and cid = %s and did = %s and status = 0;',
                     ((now_date - timedelta(days=history), now_date, cid,did)))
        conn.rollback()
    conn.close()
    return historydata

class metrics():
    def __init__(self,predict_v,true_v):
        self.predict_v = predict_v
        self.true_v = true_v
    def rmse(self):
        return np.sqrt(mean_squared_error(self.predict_v,self.true_v))
    def mse(self):
        return mean_squared_error(self.predict_v,self.true_v)

class pipline():
    def __init__(self):
        #现有模型字典，{'lstm': <class 'forecastPOS.algorithm.lstm.LstmForecast'>, 'deepModel': <class 'forecastPOS.algorithm.dnn_factory.DeepModel'>}
        self.model_factory = ClassFactory.subclasses_dict(DeepModel)
        print('model_factory',self.model_factory)
        self.model_conf = PosAutoConfig.model_conf
        self.train_conf = PosAutoConfig.train_conf #加载要训练的模型的配置信息
        print('train_conf',self.train_conf)

    #训练模型
    def train(self):
        now_date = datetime.now().date()
        for cid in self.train_conf.keys(): #各客户的cid
            for did in self.train_conf[cid].keys():  # 配置文件中各cid下的did
                print("客户{},需训练的门店:{}".format(cid, did))
                raw = getBasePos(cid, did,now_date,self.train_conf[cid][did]['history'])
                print(raw.head())
                if raw.empty: #如果历史数据为空则无法训练
                    print("cid:{}，did:{} 无历史数据，无法训练".format(cid,did))
                    infoLog.warning("cid:{}，did:{} 无历史数据，无法训练".format(cid,did))
                    continue
                else:
                    raw.loc[:, 'shike'] = pd.to_datetime(raw.loc[:, 'shike'])
                    raw = raw.set_index("shike")
                    raw = raw.resample(rule="15min", label='right', closed='right').sum()
                    for preType in self.train_conf[cid][did]['preType']:
                        df = raw[[preType]]
                        print(df.head())
                        if df.shape[0] < self.train_conf[cid][did]['min_datanums']: #30*96
                            print(did,df.shape)
                            print("cid:{},did:{},preType:{}的数据量少于设置的最小数据量，无法训练".format(cid,did,preType))
                            infoLog.warning("cid:{},did:{},preType:{}的数据量少于设置的最小数据量，无法训练".format(cid,did,preType))
                            continue
                        else:
                            #训练配置文件中指定的模型
                            for model_name in self.train_conf[cid][did]['model_name']:
                                model = self.model_factory[model_name]  # 根据模型名称加载指定的模型类，如<class 'forecastPOS.algorithm.lstm.LstmForecast'>
                                print(model)
                                #开始训练模型
                                model_instance = model(cid,did,preType)
                                message ={"train": df}
                                model_instance.train(message)


    def train_seq2seq(self,input_path,name,preType):
        data = pd.read_csv(input_path,index_col=0)
        df = data[[preType]]
        train_df = df[: '2019-12-01']
        test_df  =  df['2019-12-01':'2019-12-08']
        model_conf = PosAutoConfig.model_conf[name]
        model = self.model_factory[name]
        model_instance = model(0, 1, preType)
        message = {"train":train_df,"test":test_df}
        model_instance.train(message)

    #用训练好的模型，预测数据
    def process(self,input_path,name,preType):
        data = pd.read_csv(input_path, index_col=0)
        df = data[[preType]]
        train_df = df[:"2019-01-01"]
        test_df = df['2019-12-01':'2019-12-08']
        model = self.model_factory[name]
        model_instance = model(0, 1, preType)
        init_input = train_df[-(self.model_conf['req_days']* self.model_conf["day_seq_len"]):]
        print(init_input)
        message = {"startPreDay": '2019-12-01',
                   "endPreDay": '2019-12-08',
                   "data":init_input}
        res = model_instance.process(message)
        print(len(test_df[message["startPreDay"]:message['endPreDay']]))

        metrics_(res,test_df[message["startPreDay"]:message['endPreDay']],
                 message["startPreDay"],message["endPreDay"])

def metrics_(predict,test_df,start,end):
    predict_v = []
    true_v = []
    for key in predict.keys():

        predict_v.append(predict[key])
        true_v.append(test_df.loc[key+":00"].values[0])
    rmse = metrics(predict_v, true_v).rmse()
    print("start:{}-end:{} rmse:{}".format(start,end,rmse))

#训练模型，即要执行的定时任务在这里
def train(arg):
    print('*********{}'.format(arg))
    pip = pipline()
    pip.train()
    #pip.process()

def test():
    pip = pipline()
    pip.process()


if __name__ == "__main__":
    scheduler = TornadoScheduler()
    #scheduler.add_job(train,'date', run_date=datetime(2020, 5, 11,21,7,0), args=['定时自动训练模型'])
    #从2020-05-09开始，每周六凌晨2点训练一次模型
    scheduler.add_job(train, 'interval', weeks=1, start_date='2020-05-09 02:00:00', end_date='2020-12-31 21:30:00', args=['每周六凌晨2点定时自动训练模型'])
    scheduler.start()
    print('[Scheduler Init]APScheduler has been started]')

    IOLoop.current().start()