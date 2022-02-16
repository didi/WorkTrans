import datetime
import  pandas  as pd


def predictByAvg(cls, predictType, startPreDay, cycleDays):
    startPreTime = datetime.datetime.strptime(startPreDay, '%Y-%m-%d')  #
    print(startPreTime)
    for i in range(96 * cycleDays):
        # 在startPreDay的基础上分别加上这么多个15分钟
        pass
    avgData = {}

    return avgData



if __name__ == '__main__':
    cycleDays=1000
    pd.set_option('display.max_columns', 200)
    pd.set_option('display.max_rows', 200)
    ts  = pd.date_range(start='2018-01-01 00:00:00', periods=cycleDays * 96, freq='15min').map(str).tolist()
    ts2 = pd.date_range(start='2018-01-01 00:15:00', periods=cycleDays * 96, freq='15min').map(str).tolist()
    for ind,i in enumerate(ts):
        s=i[0:16].replace(' ',',')+','+ts2[ind][11:16]
        m=s.replace('23:45,00:00','23:45,23:60')
        print(m)
