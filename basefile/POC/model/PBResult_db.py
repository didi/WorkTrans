"""
by lyy
2019-10-20
喔趣-阶段四接口6-获取排班结果
"""
import pymysql

from config.db import conf
from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
import datetime
from dateutil.relativedelta import *
from collections import Counter

class PBResultDB:
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
            cls.connection = pymysql.Connection(
                host=cls.host,
                database=cls.database,
                user=cls.user,
                password=cls.pwd,
                charset='utf8'
            )
            return cls.connection
        except pymysql.DatabaseError:
            return None

    @classmethod
    #获取某天的任务排班矩阵
    def select_record(cls, cid, did,date,mode):
        flag = True
        res = []
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT task_matrix,id_li,split_rule,indirect_task FROM task_matrix_lyy WHERE cid=%s AND did=%s AND forecast_date=%s AND status=1 AND data_type=%s;"
        try:
            cursor.execute(sql, (cid, did, date,mode))
            resu = cursor.fetchone()
            res.append(resu[0])
            res.append(resu[1])
            res.append(resu[2])
            res.append(resu[3])
        except Exception:
            infoLog.warning(
                'FAILED, sql: SELECT task_matrix,id_li,split_rule,indirect_task FROM task_matrix_lyy WHERE cid=%s AND did=%s AND forecast_date=%s AND status=1 AND data_type=%s;',
                cid, did, date,mode)
            flag = False  # 数据库操作失败
            conn.rollback()

        conn.close()
        return res,flag

    @classmethod
    # 获取某部门的班次模板数据
    def select_shiftMod(cls, cid, did,shiftid):
        flag = True
        res = ()
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT shift_start,shift_end,is_cross_day FROM shift_mod_data WHERE cid=%s AND did=%s AND status=1 AND shiftbid=%s;"
        try:
            cursor.execute(sql, (cid, did,shiftid))
            res = cursor.fetchone()
            # for r in result:
            #     res[r[0]] = (str(r[1]),str(r[2]),r[3])
        except Exception:
            infoLog.warning(
                'FAILED, sql: SELECT shift_start,shift_end,is_cross_day FROM shift_mod_data WHERE cid=%s AND did=%s AND status=1;',
                cid, did,shiftid)
            flag = False  # 数据库操作失败
            conn.rollback()

        conn.close()
        return res, flag


    @classmethod
    # 获取当前员工可用时间
    def select_empAvailableTime(cls,cid,date):
        res = {}#{eid:[type,(s,e),(s,e)],eid:[],...}
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT eid,`type`,`start`,`end` FROM sch_available_time WHERE cid=%s AND `day`=%s AND status=1;"
        #try:
        cursor.execute(sql, (cid, date))
        ress = cursor.fetchall()
        for r in ress:
            if r[0] not in res:
                res[r[0]] = [r[1]]
                res[r[0]].append((str(r[2]),str(r[3])))
            else:
                res[r[0]].append((str(r[2]), str(r[3])))
        #
        # except Exception:
        #     infoLog.warning(
        #         'FAILED, sql: SELECT `type` FROM sch_available_time WHERE cid=%s AND eid=%s AND day=%s AND status=1;',
        #         cid, eid, date)
        #     flag = False  # 数据库操作失败
        #     conn.rollback()

        conn.close()
        return res

    @classmethod
    #获取任务对应的技能ID，列表(一个任务有可能对应多个技能)
    def select_skillID(cls,taskID,cid, did):
        flag = True
        res = []
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT taskSkillBid FROM labor_task WHERE cid=%s AND did=%s AND bid=%s AND status=1;"
        try:
            cursor.execute(sql, (cid, did, taskID))
            resu = cursor.fetchall()
            for id in resu:
                res.append(id[0])
        except Exception:
            infoLog.warning(
                'FAILED, sql: SELECT taskSkillBid FROM labor_task WHERE cid=%s AND did=%s AND bid=%s AND status=1;',
                cid, did, taskID)
            flag = False  # 数据库操作失败
            conn.rollback()

        conn.close()
        return res, flag

    @classmethod
    # 获取任务对应的证书名称列表
    def select_certsname(cls, taskID, cid, did):
        flag = True
        res = []
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT certs FROM labor_task WHERE cid=%s AND did=%s AND bid=%s AND status=1;"
        try:
            cursor.execute(sql, (cid, did, taskID))
            res = cursor.fetchone()[0].split[',']#"健康证，厨师证"

        except Exception:
            infoLog.warning(
                'FAILED, sql: SELECT certs FROM labor_task WHERE cid=%s AND did=%s AND bid=%s AND status=1;',
                cid, did, taskID)
            flag = False  # 数据库操作失败
            conn.rollback()

        conn.close()
        return res, flag

    @classmethod
    #获取技能对应的员工ID
    def select_empID(cls,skillID,cid):
        flag = True
        empid = [] #[员工ID,...]
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT eid FROM emp_skill WHERE cid=%s AND skill=%s AND status=1;"
        for id in skillID:
            try:
                cursor.execute(sql, (cid, id))
                res = cursor.fetchall()
                for e in res:
                    empid.append(e[0])

            except Exception:
                infoLog.warning(
                    'FAILED, sql: SELECT eid FROM emp_skill WHERE cid=%s AND skill=%s AND status=1;',
                    cid, id)
                flag = False  # 数据库操作失败
                conn.rollback()

        emps_li = [str(k) for k, v in dict(Counter(empid)).items() if v == len(skillID)]  # 找出每个证书都有的员工
        conn.close()
        return emps_li, flag

    @classmethod
    # 获取拥有所需证书的员工ID列表
    def select_empID_certs(cls, certname_li, cid):
        conn = cls.get_connection()
        empid = []  # [员工ID,...]
        flag = True
        for cn in certname_li:

            cursor = conn.cursor()
            sql = "SELECT eid FROM employee_certificate WHERE cid=%s AND certname=%s AND status=1;"
            try:
                cursor.execute(sql, (cid, cn))
                res = cursor.fetchall()
                for e in res:
                    empid.append(e[0])

            except Exception:
                infoLog.warning(
                    'FAILED, sql: SELECT eid FROM employee_certificate WHERE cid=%s AND certname=%s AND status=1;',
                    cid, cn)
                flag = False  # 数据库操作失败
                conn.rollback()
        emps_li = [str(k) for k, v in dict(Counter(empid)).items() if v == len(certname_li)]#找出每个证书都有的员工
        conn.close()
        return emps_li, flag

    @classmethod
    # 获取指定员工对应的技能ID和技能值
    def select_empSkills(cls, eid, cid):
        flag = True
        emp_skilldata = {}  # {技能ID：技能值,技能ID：技能值,...}
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT skill,skillNum FROM emp_skill WHERE cid=%s AND eid=%s AND status=1;"
        try:
            cursor.execute(sql, (cid, eid))
            res = cursor.fetchall()
            for e in res:
                if len(e) != 0:
                    emp_skilldata[e[0]] = e[1]

        except Exception:
            infoLog.warning(
                'FAILED, sql:SELECT skill,skillNum FROM emp_skill WHERE cid=%s AND eid=%s AND status=1;',
                cid, eid)
            flag = False  # 数据库操作失败
            conn.rollback()

        conn.close()
        return emp_skilldata, flag

    @classmethod
    # 获取指定员工对应的证书和截止日期
    def select_empCerts(cls, eid, cid):
        flag = True
        emp_certdata = {}  # {证书名称：到期日期,证书名称：到期日期,...}
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT certname,closingdate FROM employee_certificate WHERE cid=%s AND eid=%s AND status=1;"
        try:
            cursor.execute(sql, (cid, eid))
            res = cursor.fetchall()
            for e in res:
                if len(e) != 0:
                    emp_certdata[e[0]] = str(e[1])

        except Exception:
            infoLog.warning(
                'FAILED, sql:SELECT certname,closingdate FROM employee_certificate WHERE cid=%s AND eid=%s AND status=1;',
                cid, eid)
            flag = False  # 数据库操作失败
            conn.rollback()

        conn.close()
        return emp_certdata, flag

    @staticmethod
    def start_end(start,days):
        start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        i = 1
        end = start
        while i < days:  # 周期范围，增加几天
            i += 1
            end += datetime.timedelta(days=1)  # 加一天
        return str(start),str(end)

    @staticmethod
    def emp_caution(cycle,start,days,shiftTime_rule,lx,num,caution,shiftid,cret):
        if cycle == 'day':  # cycle是day
            #start, end = PBResultDB.start_end(start, days)
            shiftTime_rule[caution].append((start + '*' + start,lx, num, shiftid, cret,cycle))
        elif cycle == 'week':  # cycle是week
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end = start + relativedelta(weeks=+1)
            end = end - relativedelta(days=+1)
            shiftTime_rule[caution].append((str(start) + '*' + str(end), lx, num, shiftid, cret,cycle))
        elif cycle == 'month':  # cycle是month
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end = start + relativedelta(months=+1)
            end = end - relativedelta(days=+1)
            shiftTime_rule[caution].append((str(start) + '*' + str(end), lx, num, shiftid, cret,cycle))
        else:# cycle == '': #cycle为空，证书规则里cycle就是空
            #end = start = datetime.strptime(start, '%Y-%m-%d').date()
            shiftTime_rule[caution].append((str(start) + '*' + str(start), lx, num, shiftid, cret,''))
        return shiftTime_rule

    @staticmethod
    def org_caution(cycle, start, days, shiftTime_rule, lx, num, caution):
        if cycle == 'day':  # cycle是day
            start, end = PBResultDB.start_end(start, days)
            shiftTime_rule[caution].append((start + '*' + end, lx, num))
        elif cycle == 'week':  # cycle是week
            start, end = PBResultDB.start_end(start, days*7)
            #start = datetime.datetime.strptime(start, '%Y-%m-%d').weekday()
            # end = start + relativedelta(weeks=+1)
            shiftTime_rule[caution].append((str(start) + '*' + str(end), lx, num))
        elif cycle == 'month':  # cycle是month
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end = start + relativedelta(months=+1)
            shiftTime_rule[caution].append((str(start) + '*' + str(end), lx, num))
        return shiftTime_rule

    @classmethod
    # 获取某员工合规性规则
    def select_emphgrule(cls, cid,eid_list):
        #rule:{'shiftTime':{'hint':【（'开始*结束'，比较类型,数值,shiftid,certname）】,'warning':[比较类型,数值,shiftid,certname],
        #                               'forbid':[（开始*结束，比较类型,数值,shiftid,certname）,...]},
        #      'shiftLen':{},...
        #                }

        emp_rules = {}#规则列表
        conn = cls.get_connection()
        cursor = conn.cursor()
        for eid in eid_list:
            eid_rule = {}
            emp_ruleTag = ['shiftTime','shiftLen','interval','schShiftNum','apShiftNum','schDayNumCon','restNumCon','noSchNum','schNumSame','restNum','certExpireDays']
            for rt in emp_ruleTag:
                sql = "SELECT caution,startDate,cycle,timeRange,ruleCpType,ruleCpNum,shiftId,cret FROM sch_compliance WHERE cid=%s AND ruleTag=%s " \
                      "AND status=1 AND eid=%s AND ptype = 'emprule';"

                #try:
                cursor.execute(sql, (cid,rt,eid))
                shiftTime_res = cursor.fetchall()
                rule = {'hint':[],'warning':[],'forbid':[]}
                if len(shiftTime_res) != 0:
                    for r in shiftTime_res:
                        if len(r) != 0:
                            if r[0] == 'hint':#hint 提示, forbid 禁止，warning 警告
                                if r[3] != '':
                                    t = int(r[3])
                                rule = PBResultDB.emp_caution(r[2],str(r[1]),t,rule,r[4],r[5],'hint',r[6],r[7])
                            elif r[0] == 'warning':
                                if r[3] != '':
                                    t = int(r[3])
                                rule = PBResultDB.emp_caution(r[2],str(r[1]),t,rule,r[4],r[5],'warning',r[6],r[7])
                            elif r[0] == 'forbid':
                                if r[3] != '':
                                    t = int(r[3])
                                rule = PBResultDB.emp_caution(r[2],str(r[1]), t, rule, r[4], r[5],'forbid',r[6],r[7])

                    eid_rule[rt] = rule
                    emp_rules[eid] = eid_rule


            # except Exception:
            #     flag = False  # 数据库操作失败
            #     conn.rollback()

        conn.close()
        return emp_rules

    @classmethod
    # 获取某部门合规性规则
    def select_orghgrule(cls, did, cid):
        # {'ruletag':{'forbid':[('开始*结束',比较类型,数值),()],'hint':[('开始*结束',比较类型,数值),()],...},
        #      ,'ruletag2':{},...}
        # 技能需求时，ruletag-技能ID；证书需求时，ruletag-证书名称；班次需求时，ruletag-班次ID
        flag = True
        org_rules = {}
        conn = cls.get_connection()
        cursor = conn.cursor()
        #organize_ruleTag = ['skilldemand', 'cretdemand', 'shiftdemand']

        #for rt in organize_ruleTag:
        sql = "SELECT caution,startDate,cycle,timeRange,ruleCpType,ruleCpNum,ruleTag FROM sch_compliance" \
              " WHERE cid=%s AND did=%s AND status=1 AND ptype = 'organizerule';"

        try:
            cursor.execute(sql, (cid, did))
            shiftTime_res = cursor.fetchall()
            org_rules = {}
            for r in shiftTime_res:
                ruletag = r[6]
                if ruletag not in org_rules:
                    d_rule = {'hint':[],'warning':[],'forbid':[]}
                    if r[0] == 'hint':
                        shiftTime_rule = PBResultDB.org_caution(r[2], str(r[1]), int(r[3]), d_rule, r[4],r[5], 'hint')
                    elif r[0] == 'warning':
                        shiftTime_rule = PBResultDB.org_caution(r[2], str(r[1]), int(r[3]), d_rule, r[4],r[5], 'warning')
                    elif r[0] == 'forbid':
                        shiftTime_rule = PBResultDB.org_caution(r[2], str(r[1]), int(r[3]), d_rule, r[4],r[5], 'forbid')
                else:
                    d_rule = org_rules[ruletag]
                    if r[0] == 'hint':
                        shiftTime_rule = PBResultDB.org_caution(r[2], str(r[1]), int(r[3]), d_rule, r[4],r[5], 'hint')
                    elif r[0] == 'warning':
                        shiftTime_rule = PBResultDB.org_caution(r[2], str(r[1]), int(r[3]), d_rule, r[4],r[5], 'warning')
                    elif r[0] == 'forbid':
                        shiftTime_rule = PBResultDB.org_caution(r[2], str(r[1]), int(r[3]), d_rule, r[4],r[5], 'forbid')
                org_rules[ruletag] = shiftTime_rule
                print('shiftTime_rule',shiftTime_rule)

        except Exception:
            flag = False  # 数据库操作失败
            conn.rollback()
            #org_rules.update(o_rules)
        conn.close()
        return  org_rules, flag

    @classmethod
    # 获取匹配规则
    def select_rule(cls, did, cid, weight):
        flag = True
        ruledata = []  # [(规则名称，比较类型，比较数值)]
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT ruletag,ruleCpType,ruleCpNum FROM emp_matchpro WHERE cid=%s AND did=%s AND status=1 AND weight=%s;"
        try:
            cursor.execute(sql, (cid, did, weight))
            res = cursor.fetchone()
            ruledata.append(res)

        except Exception:
            infoLog.warning(
                'FAILED, sql:SELECT ruletag,ruleCpType,ruleCpNum FROM emp_matchpro WHERE cid=%s AND did=%s AND status=1 AND weight=%s;',
                cid, did, weight)
            flag = False  # 数据库操作失败
            conn.rollback()

        conn.close()
        return ruledata, flag

    @classmethod
    def select_skillName(cls,cid, did):
        flag = True
        res = {}
        conn = cls.get_connection()
        cursor = conn.cursor()
        sql = "SELECT bid,taskName FROM labor_task WHERE cid=%s AND did=%s AND status=1;"
        try:
            cursor.execute(sql, (cid, did))
            rr = cursor.fetchall()
            for r in rr:
                res[r[0]] = r[1]

        except Exception:
            infoLog.warning(
                'FAILED, sql: SELECT taskSkillBid FROM labor_task WHERE cid=%s AND did=%s AND bid=%s AND status=1;',
                cid, did)
            flag = False  # 数据库操作失败
            conn.rollback()

        conn.close()
        return res, flag

if __name__ == '__main__':
    # org_rules, flag = PBResultDB().select_orghgrule('6','123456')
    # print(len(org_rules))
    # print(org_rules)
    # res, flag = PBResultDB.select_skillName('123456','6')
    # print(res)

    emp_rules = PBResultDB().select_emphgrule('50000031', ['11019'])
    print(emp_rules)