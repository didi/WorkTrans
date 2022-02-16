import datetime
import  pandas  as pd



if __name__ == '__main__':
    '''
    生成需要的base天数的key值 【2019-01-01 00：15：00】、【2019-01-01 00：30：00】、【2019-01-01 00：45：00】
    '''

    cycleDays=1
    pd.set_option('display.max_columns', 200)
    pd.set_option('display.max_rows', 200)

    startBaseDay='2018-01-01 00:00'

    startBaseDaySeq  = pd.date_range(start=startBaseDay, periods=cycleDays * 96, freq='15min').tolist()
    startBaseDayKey=list(map(lambda x:str(x)[0:16],startBaseDaySeq))
    print(startBaseDayKey)
