import pymysql


class QuerySettingsDBModel():

    @classmethod
    def setQuerySettings(self, cid,companyName,periodicType,weekIndex,startDay,dayCount,note,effectStartDate,EffectEndDate):
        """
        设置查询参数
        :param cid:
        :param companyName:
        :param periodicType:
        :param weekIndex:
        :param startDay:
        :param dayCount:
        :param note:
        :param effectStartDate:
        :param EffectEndDate:
        :return:
        """


        sql = """insert into base_pos_query_settings_df(cid,companyName,periodicType,weekIndex,startDay,dayCount,note,effectStartDate,EffectEndDate) values(%s,%s,%s,%s,%s,%s,%s,%s,%s);"""


        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='Ybaobao1', db='woqu')

        cursor = conn.cursor()
        cursor.execute(sql,(cid,companyName,periodicType,weekIndex,startDay,dayCount,note,effectStartDate,EffectEndDate))
        conn.commit()
        cursor.close()
        conn.close()
        return True





