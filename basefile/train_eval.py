import numpy as np
import pandas as pd
import sys
#sys.path.append("/Users/didi/feng/didi_code/woqu20200421/woqu/basefile/")
print(sys.path)
from forecastPOS.algorithm.lstm import DeepModel
from forecastPOS.algorithm.prophet import ProphetForecast
from forecastPOS.algorithm.seq2seq import seq2seqForecast
import argparse
from forecastPOS.algorithm.dnn_factory import ClassFactory
from config.pos_auto_conf import PosAutoConfig
from sklearn.metrics import mean_squared_error

class metrics():
    def __init__(self,predict_v,true_v):
        self.predict_v = predict_v
        self.true_v = true_v
    def rmse(self):
        return np.sqrt(mean_squared_error(self.predict_v,self.true_v))
    def mse(self):
        return mean_squared_error(self.predict_v,self.true_v)

class pipline():
    def __init__(self,name):
        self.model_factory = ClassFactory.subclasses_dict(DeepModel)
        self.model_conf = PosAutoConfig.model_conf.get(name,{})
    def train(self,input_path,model_name,preType):
        raw = pd.read_csv(input_path)
        print(raw.columns)
        did_arr = np.unique(raw.did).tolist()
        cid_arr = np.unique(raw.cid).tolist()
        if len(cid_arr)>1:
            print("非同一家客户")
            return
        print("客服{},训练数据中的门店:{}".format(cid_arr,did_arr))

        cid = cid_arr[0]
        for did in did_arr[0:1]:
            df = raw[raw.did==did]
            if df.shape[0]< 30*96:
                print(did,df.shape)
                print("did:{} 数据量少于一个月的数据，无法训练".format(did))
                continue
            df["shike"] = pd.to_datetime(df["shike"])
            df = df.set_index("shike")
            df = df.resample(rule="15min",label='right', closed='right').sum()
            data = df[[preType]]
            print(data.head())
            model = self.model_factory[model_name]
            model_instance = model(cid,did,preType)
            message ={"train": data}
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


def train(input_path,model_name, preType):
    pip =  pipline(model_name)
    pip.train(input_path,model_name,preType)
    pip.process(input_path,model_name,preType)

def test(input_path,model_name, preType):
    pip = pipline(model_name)
    pip.process(input_path,model_name,preType)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="train and eval")
    parser.add_argument("--model_name", type=str, default="seq2seq", help="server port")
    parser.add_argument("--input_path", type=str, default='799new.csv', help="输入文件的路径")
    parser.add_argument("--mode", type=str, default="train", help="train or test")
    parser.add_argument("--preType",type=str, default="truePeoples",help="预测的类型，客流量，订单量")

    args = parser.parse_args()
    if args.mode == "train":
        train(args.input_path,args.model_name,args.preType)
    elif args.mode == "test":
        test(args.input_path,args.model_name,args.preType)
    else:
        raise NameError

