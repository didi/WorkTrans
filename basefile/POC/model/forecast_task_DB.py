'''
create by liyabin
'''

import pymysql
import datetime
from typing import Tuple,Dict,List,Set
from config.db import conf
from utils.myLogger import infoLog
from utils.testDBPool import DBPOOL

class ForecastTaskDB:
    db_config = conf.db['mysql']
    host = db_config['host']
    port = db_config['port']
    user = db_config['user']
    pwd = db_config['password']
    database = db_config['database']
    connection = None

    @classmethod
    def __del__(cls):
        if cls.connection:
            cls.close()

    @classmethod
    def close(cls):
        try:
            cls.connection.close()
        except Exception:
            pass

    @classmethod
    def get_connection(cls):
        try:
            # cls.connection = pymysql.Connection(
            #     host=cls.host,
            #     database=cls.database,
            #     user=cls.user,
            #     password=cls.pwd,
            #     charset='utf8'
            # )
            cls.connection = DBPOOL.connection()
            return cls.connection
        except pymysql.DatabaseError:
            return None

    @classmethod
    def insert_record(cls, taskCombination:str, combinationVal:str, taskId:str,
                      taskType:str,work_date:str, start:str, end:str):
        '''
        第三阶段结果存储到数据库
        :param taskCombination:
        :param combinationVal:
        :param taskId:
        :param taskType:
        :param work_date:
        :param start:
        :param end:
        :return:
        '''
        res_flag = False
        now_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                        INSERT INTO comb_tasks(taskCombination,combinationVal,taskId,taskType,work_date,start,end,create_time,update_time,status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """
            try:
                cursor.execute(sql, (
                taskCombination,combinationVal,taskId,taskType,work_date,start,end,
                now_datetime, now_datetime, '1'))
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
                res_flag = False
        conn.close()
        return res_flag

    @classmethod
    def read_worktime_rule(cls,ptype:str,cid:str,eid:str,startDate:str,ruleType:str,ruletag:str,cycle:str) -> Tuple:
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                                SELECT cid,eid,ruleType,cycle,timeRange,startDate,ruletag,ruleCpType,ruleCpNum,dayFusion,shiftId,cret,caution from sch_compliance
                                where ptype=%s and cid = %s and eid = %s and startDate=%s and ruleType=%s and ruletag=%s and cycle=%s and status=1
                                """
            try:
                cursor.execute(sql, (
                    ptype,cid,eid,startDate,ruleType,ruletag,cycle))

                result = cursor.fetchall()

                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_all_rule(cls,cid:str) -> Tuple:
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                                SELECT ptype,cid,eid,did,ruleType,ruleCpType,ruletag,ruleCpNum,startDate,dayFusion,cycle,timeRange,shiftId,cret,caution,bid 
                                from sch_compliance
                                where  status=1 and cid=%s
                                """
            try:
                cursor.execute(sql,cid)
                result = cursor.fetchall()

                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_lxpb_rule(cls, cid: str,bid:str) -> Tuple:
        conn = cls.get_connection()
        r = -1
        t ='1991-01-01'
        with conn.cursor() as cursor:
            sql = """
                SELECT ruleCpNum,startDate from sch_compliance where  status=1 and cid=%s and bid=%s and ruletag='schDayNumCon' 
                and ptype='emprule' and caution='forbid'
                """
            try:
                cursor.execute(sql, (cid,bid))
                result = cursor.fetchall()
                if result:
                    r = result[0][0]
                    t = result[0][1]
                conn.commit()
            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return r,t

    @classmethod
    def read_emp_matchtpro(cls,cid:str):
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                               SELECT * FROM emp_matchpro where status=1 and cid=%s;
                                                """
            try:
                cursor.execute(sql,cid)
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_emp_info(cls,cid:str,forecast_day:str):

        conn = cls.get_connection()
        result = None
        with conn.cursor() as cursor:
            sql = """select a.cid,a.eid,a.type,a.starts,a.ends,a.day,a.skills,a.skillNums,ec.certname,ec.closingdate from
                    (select at.cid,at.eid,at.type,at.starts,at.ends,at.day,sk.skills,sk.skillNums from 
                        (select sa1.cid cid,sa1.eid eid,sa2.type type,sa1.starts starts,sa1.ends ends,sa2.day day
                            from (SELECT cid,eid,group_concat(start) starts,group_concat(end) ends FROM sch_available_time where status=1 and day=%s and cid=%s group by cid,eid) sa1,(select cid cid,eid eid,type type,day day from sch_available_time where status=1 group by cid,eid,type,day) sa2 
                                    where sa1.cid=sa2.cid and sa1.eid=sa2.eid and sa2.day=%s) at 
                            left join (SELECT cid,eid,group_concat(skill) skills,group_concat(skillNum) skillNums 
                                        FROM emp_skill 
                                        where status=1 group by cid,eid) as sk 
                            on sk.cid=at.cid and sk.eid=at.eid where at.day=%s) a
                    left join (select cid,eid,certname,closingdate from employee_certificate where status=1) ec on ec.cid=a.cid and ec.eid=a.eid;"""
            try:
                cursor.execute(sql,(forecast_day,cid,forecast_day,forecast_day))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_taskName_of_labor_task(cls, cid: str):
        '''
        任务详情  taskName - taskBid
        :param cid:
        :return:
        '''
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                                       SELECT bid,taskName,taskSkillBid FROM labor_task where status=1 and cid=%s;
                                                        """
            try:
                cursor.execute(sql, cid)
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_laborTask_info(cls,cid:str,did:str):
        '''
        任务详情
        :param cid:
        :return:
        '''
        conn = cls.get_connection()
        result = None
        with conn.cursor() as cursor:
            #数据格式：a.cid,a.did,a.bid,b.taskName,b.abCode,b.taskType,b.worktimeType,b.worktimeStart,b.worktimeEnd,a.taskSkillBids,a.skillNums,a.certs
            #        ('123456', '6', '201903291236061290061007959f0209', '吧台', 'SY', 'directwh', 'bisTime', datetime.timedelta(0, 28800), datetime.timedelta(0, 79200)
            sql = """
                    select a.cid,a.did,a.bid,b.taskName,b.abCode,b.taskType,b.worktimeType,b.worktimeStart,b.worktimeEnd,a.taskSkillBids,a.skillNums,a.certs
                    from (SELECT cid,bid,did,group_concat(taskSkillBid) taskSkillBids,group_concat(skillNum) skillNums,group_concat(distinct cert) certs FROM labor_task where status=1 and cid=%s and did=%s group by cid,bid,did order by cid,did,bid) a
                    left join labor_task b 
                    on a.cid=b.cid and a.bid=b.bid and a.did = b.did
                    where b.status=1 
                    group by a.cid,a.did,a.bid,b.taskName,b.abCode,b.taskType,b.worktimeType,b.worktimeStart,b.worktimeEnd,a.taskSkillBids,a.skillNums,a.certs
                    order by a.cid,a.did,a.bid;
                                                                """
            try:
                cursor.execute(sql, (cid,did))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_laborTask_for_temp_emp(cls,cid:str,did:str) -> Tuple:
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            # 数据格式：a.cid,a.did,a.bid,b.taskName,b.abCode,b.taskType,b.worktimeType,b.worktimeStart,b.worktimeEnd,a.taskSkillBids,a.skillNums,a.certs
            #        ('123456', '6', '201903291236061290061007959f0209', '吧台', 'SY', 'directwh', 'bisTime', datetime.timedelta(0, 28800), datetime.timedelta(0, 79200)
            sql = """
            select `cid`,`did`,`bid`,`fillCoefficient`,`discard`,`taskMinWorkTime`,`taskMaxWorkTime` from labor_task
            where cid=%s and did=%s and status=1
            """
            try:
                cursor.execute(sql, (cid, did))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_emp_matchpro(cls,cid:str,did:str):
        '''
        匹配属性
        :param cid:
        :param did:
        :return:
        '''
        conn = cls.get_connection()
        with conn.cursor() as cursor:

            sql = """
                    select cid,did,weight,ruleGroup,ruleCpType,ruletag,ruleCpNum from emp_matchpro where status=1 and cid=%s and did=%s
                                                                        """
            try:
                cursor.execute(sql, (cid,did))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result


    @classmethod
    def read_matrix(cls,cid:str,did:str,start_date:str,end_date:str,forecastType:str,type='full'):
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = """
                                    SELECT cid,did,forecast_date,start_time,end_time,task_matrix from task_matrix_ss WHERE cid=%s AND did=%s AND forecastType=%s AND `type`=%s AND forecast_date>=%s and forecast_date<=%s and status=1;
                                    """
            try:
                cursor.execute(sql, (cid, did,forecastType,type, start_date,end_date))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @classmethod
    def read_labor_shift_split_rule(cls,cid:str,did:str):
        '''
        读取拆分规则
        :param cid:
        :return:
        '''
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = " SELECT cid,did,ruleCalType,ruleCpType,ruleCpNum,dayFusion FROM labor_shift_split_rule where status=1 and  cid =%s  and did = %s ;"

            try:
                cursor.execute(sql,(cid,did))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @staticmethod
    def read_labor_shift_split_rule_to_list(cid:str,did:str):
        labor_shift_split_info:Tuple = ForecastTaskDB.read_labor_shift_split_rule(cid=cid,did=did)

        shiftsplitData :List = []

        for item in labor_shift_split_info:
            labor_shift_split_dict = {}

            labor_shift_split_dict['ruleCalType'] = item[2]
            labor_shift_split_dict['ruleCpType'] = item[3]
            labor_shift_split_dict['ruleCpNum'] = item[4]
            labor_shift_split_dict['dayFusion'] = item[5]

            shiftsplitData.append(labor_shift_split_dict)

        labor_shift_split_rule = [{"shiftsplitbid": "", "didArr": [did], 'shiftsplitData': shiftsplitData}]

        return labor_shift_split_rule


    @classmethod
    def read_comb_rule(cls,cid:str,did:str):
        '''
                读取组合规则
                :param cid:
                :return:
                '''
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = "SELECT cid,did,rule_data FROM labor_comb_rule where status=1 and cid = %s and did = %s;"

            try:
                cursor.execute(sql,(cid,did))
                result = cursor.fetchall()
                conn.commit()

            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @staticmethod
    def read_comb_rule_to_list(cid: str, did: str):
        combirule = {'combiruleBid': '', 'didArr': [did], 'combiRuleData': []}
        result = ForecastTaskDB.read_comb_rule(cid, did)
        for c, d, data in result:
            combirule['combiRuleData'].append({'ruleData': data})
        res = [combirule]
        return res

    @classmethod
    def read_shift_mod(cls, cid: str, did: str):
        '''
        读取班次模板
        :param cid:
        :param did:
        :return:
        '''
        result = None
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            sql = "SELECT cid,did,bid,shiftbid,shift_start,shift_end,is_cross_day FROM shift_mod_data where status=1 and cid = %s and did = %s;"
            try:
                cursor.execute(sql, (cid, did))
                result = cursor.fetchall()
                conn.commit()
            except Exception:
                infoLog.warning(
                    'FAILED, sql: %s' % sql)
                conn.rollback()
        conn.close()
        return result

    @staticmethod
    def read_shift_mod_to_list(cid: str, did: str):
        shift_mod_data = ForecastTaskDB.read_shift_mod(cid=cid, did=str(did))

        shiftModbid = ""
        didArr = [did]

        shiftModData = []
        # cid,did,bid,shiftbid,shift_start,shift_end,is_cross_day
        for s in shift_mod_data:
            shiftModbid = s[2]
            didArr = [did]
            shiftModData.append({
                "shiftBid": s[3],
                "shiftStart": (datetime.datetime.strptime('1990-01-01', '%Y-%m-%d') + datetime.timedelta(
                    seconds=s[4].total_seconds())).strftime('%H:%M'),
                "shiftEnd": (datetime.datetime.strptime('1990-01-01', '%Y-%m-%d') + datetime.timedelta(
                    seconds=s[5].total_seconds())).strftime('%H:%M'),
                "isCrossDay": True if s[6] != 0 else False
            })

        shift_mod_rule = {
            'shiftModbid': shiftModbid,
            'didArr': didArr,
            'shiftModData': shiftModData
        }

        return [shift_mod_rule]

    @classmethod
    def prePcrocess_empAvailable(cls,cid: str,eid:str,date:str):
        """
        获取员工可用性，若当前员工无可用性，则向表中插入该员工的可用性记录，默认全天可用(0)
        :param cid:
        :param eid:
        :param date:
        :return:
        """
        flag = True
        now = datetime.datetime.now()
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT `type`,`start`,`end` FROM sch_available_time WHERE cid=%s AND eid=%s AND `day`=%s AND status=1;"
        insert_sql = "INSERT INTO sch_available_time(cid,eid,opt,`type`,start,end,day,create_time,update_time,status) " \
                     "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            cursor.execute(sql, (cid, eid,date))
            res = cursor.fetchone()
            conn.commit()
            if res is None:
                try:
                    #cursor.execute(insert_sql,(cid,eid,'insert','0','','',date,now,now,1))
                    cursor.execute(insert_sql, (cid, eid, 'insert', '0', None, None, date, now, now, "1"))
                    conn.commit()
                except Exception:
                    infoLog.warning(
                        'FAILED, sql: %s' % insert_sql)
                    flag = False
                    conn.rollback()

        except Exception:
            infoLog.warning(
                'FAILED, sql: %s' % sql)
            flag = False
            conn.rollback()

        conn.close()
        return flag

if __name__ == '__main__':
    #result = ForecastTaskDB.read_emp_info(cid='123456',forecast_day='2019-07-12')
    #print(result)

    #print(ForecastTaskDB.read_all_rule(cid="123456"))

    #print(ForecastTaskDB.read_laborTask_info(cid="50000031",did='7692'))

    #print(ForecastTaskDB.read_emp_matchpro(cid="123456",did="6"))

    #print(ForecastTaskDB.read_matrix(cid="123456",did = "6",start_date="2019-07-12",end_date="2019-07-13"))

    #print(ForecastTaskDB.read_labor_shift_split_rule(cid='50000031',did='7692'))

    #print(ForecastTaskDB.read_comb_rule(cid='50000031',did='7692'))

    #print(ForecastTaskDB.read_comb_rule_to_list(cid='123456',did='6'))

    #print(ForecastTaskDB.read_labor_shift_split_rule_to_list(cid='123456',did='6'))

    print(ForecastTaskDB.read_shift_mod_to_list(cid='123456',did='6'))
