
from utils.testDBPool import DBPOOL
import json
from utils.myLogger import infoLog
import datetime
from tornado import gen

class HistoryShiftUtils():
    def __init__(self):
        self.cacheHistoryData = {}
        # TODO 从数据库中将所有历史排班信息缓存起来
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        selectAllsqlStr = 'SELECT * FROM inner_history_workunit where shiftId != 0 and workTime != -1 order by eid,schDay'

        try:
            count = cursor.execute(selectAllsqlStr)
            data = cursor.fetchall()
            # eid, schDay, shiftId, shiftName, startTime, endTime, workTime
            for d in data:
                # print(d)
                eid = d[3]
                schDay = d[4]
                shiftId = d[5]
                shiftName = d[6]
                startTime = d[7]
                endTime = d[8]
                workTime = d[9]
                if eid not in self.cacheHistoryData:
                    self.cacheHistoryData[eid] = {}
                if schDay not in self.cacheHistoryData[eid]:
                    self.cacheHistoryData[eid][schDay] = []
                self.cacheHistoryData[eid][schDay].append((shiftId, startTime, endTime, workTime))

        except Exception as e:
            print(e)
        print('{} 缓存历史班次信息完成' .format(HistoryShiftUtils))

    @gen.coroutine
    def getHistory(self,paramter):
        infoLog.info('HistoryGetHandller : {}'.format(paramter))
        raw_data = paramter
        queryDict = raw_data
        result = {}
        try:
            hasMiss = False
            for eid in queryDict.keys():
                result[eid] = {}
                if hasMiss:
                    break
                for schDay in queryDict[eid]:
                    if eid in self.cacheHistoryData and schDay in self.cacheHistoryData[eid]:
                        result[eid][schDay] = self.cacheHistoryData[eid][schDay]
                    else:
                        hasMiss = True
                        break
            if hasMiss:
                self.queryHistoryDataByEidsAndSchDays(queryDict)
                for eid in queryDict.keys():
                    result[eid] = {}
                    for schDay in queryDict[eid]:
                        if eid in self.cacheHistoryData and schDay in self.cacheHistoryData[eid]:
                            result[eid][schDay] = self.cacheHistoryData[eid][schDay]
                        else:
                            result[eid][schDay]=[]

            #print(result)
        except Exception as e:
            print(e)

        raise gen.Return(result)

    @gen.coroutine
    def saveShiftResult(self,paramter):
        ''' 保存排班结果

        :param param:
        :return:
        '''
        infoLog.info('HistoryPushHandler : %s' % (self.request.body.decode('utf-8')))
        s = datetime.datetime.now()

        raw_data = param
        schemes = raw_data['schemes']
        cal = raw_data['cal']
        shiftDataForInsert = []
        for eidsTask in cal:
            eid = eidsTask['eid']
            schDay = eidsTask['schDay']
            workUnit = eidsTask['workUnit']
            for unit in workUnit:
                type = unit['type']
                outId = unit['outId']
                # shiftId = unit['shiftId']
                startTime = unit['startTime']
                endTime = unit['endTime']
                # historydate = (eid,schDay,shiftId,outId, startTime, endTime, self.HHMMSSDiff(startTime, endTime))
                wh =  self.HHMMSSDiff(startTime, endTime)
                historydate = (eid, schDay, outId,outId, startTime, endTime,wh)
                # 先将数据插入到cache中

                if eid not in self.cacheHistoryData:
                   self.cacheHistoryData[eid]={}
                if schDay not in self.cacheHistoryData[eid]:
                    self.cacheHistoryData[eid][schDay]=[]
                self.cacheHistoryData[eid][schDay].append(historydate)
                shiftDataForInsert.append(historydate)
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sqlstr = 'insert into inner_history_workunit(eid,schDay,shiftId,startTime,endTime,workTime) values'
        for insertinfo in shiftDataForInsert:
            sqlstr+=r'("{}","{}","{}","{}","{}","{}"),'.format(insertinfo[0],insertinfo[1],insertinfo[2],insertinfo[3],insertinfo[4],insertinfo[5])
        sqlstr=sqlstr[:-1]
        count= cursor.execute(sqlstr)
        print(count)
        conn.close()
        print("排班结果插入数据库完成")
        raise gen.Return("ok")


    def queryHistoryDataByEidsAndSchDays(self,eidAndSchDays):

        selectAllsqlStr = 'SELECT eid,schDay,outId,startTime,endTime, workTime FROM task_schedule where status = 1 '
        wheresql = 'and'
        for eid in eidAndSchDays.keys():
            subsql = r' (eid = "{}" and '.format(eid)
            subsql+="("
            for schDay in eidAndSchDays[eid]:
                subsql+=r' schDay = "{}" or'.format(schDay)
            subsql=subsql[:-3]
            subsql+=r')'
            subsql+=r') or'
            wheresql+=subsql


        selectAllsqlStr+= wheresql
        selectAllsqlStr = selectAllsqlStr[:-3]
        #print(selectAllsqlStr)
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        cursor.execute(selectAllsqlStr)
        data = cursor.fetchall()
        for d in data:
            #print(d)
            eid = d[0]
            schDay = d[1]
            shiftId = d[2]
            # shiftName = d[]
            startTime = d[3]
            endTime = d[4]
            workTime = d[5]
            if eid not in self.cacheHistoryData:
                self.cacheHistoryData[eid] = {}
            if schDay not in self.cacheHistoryData[eid]:
                self.cacheHistoryData[eid][schDay] = []
            self.cacheHistoryData[eid][schDay].append((shiftId, startTime, endTime, workTime))
        conn.close()

    def HHMMSSDiff(self,h1,h2):
        t1 = datetime.datetime.strptime(h1, "%Y-%m-%d %H:%M:%S")
        t2 = datetime.datetime.strptime(h2, "%Y-%m-%d %H:%M:%S")
        dtl = t2 - t1
        return dtl.seconds / 60

HistoryShiftUtils = HistoryShiftUtils()
