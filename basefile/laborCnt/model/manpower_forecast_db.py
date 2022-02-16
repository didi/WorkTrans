"""
@author: liyabin
@contact: liyabin_i@didiglobal.com
@file: ManPowerCls.py
@time: 2019-09- 23：28
@desc:
"""

import json

from utils.dateUtils import DateUtils
from utils.myLogger import infoLog
from typing import List, Tuple, Dict

from utils.task import FixedTask, DirectTask, InDirectTask
from utils.testDBPool import DBPOOL
import pandas as pd


class ManPowerForecastDB:

    @classmethod
    def select_labor_task_for_id(cls, cid: str, did: str):
        dataSet = []
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        with conn.cursor() as cursor:
            sql = """
            SELECT cid,bid,did,taskType,worktimeType,worktimeStart,worktimeEnd from labor_task WHERE cid=%s AND did=%s AND status=1;
            """
            try:
                row = cursor.execute(sql, (cid, did))
                conn.commit()
                if row:
                    dataSet = cursor.fetchall()

                infoLog.debug(
                    'success, sql: SELECT cid,bid,did,taskType,worktimeType,worktimeStart,worktimeEnd from labor_task WHERE cid=%s AND did=%s AND status=1;',
                    now_datetime, cid, did)
            except Exception:
                infoLog.warning(
                    'FAILED, sql: SELECT cid,bid,did,taskType,worktimeType,worktimeStart,worktimeEnd from labor_task WHERE cid=%s AND did=%s AND status=1;;',
                    now_datetime, cid, did)
                conn.rollback()
        conn.close()
        return dataSet

    @classmethod
    def get_open_shutdown_task_id_list(cls, cid: str, did: str) -> List[str]:
        """
        获取开店打烊任务bid列表
        :param cid:
        :param did:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sql = "SELECT bid, taskName FROM labor_task WHERE cid=%s AND did=%s AND status=1;" % (cid, did)
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            infoLog.info('success: %s' % sql)
        except Exception:
            infoLog.info('falid: %s' % sql)
            res = []
        conn.close()

        result = []
        for task in res:
            bid = task[0]
            task_name = task[1]
            if '打' in task_name or '开' in task_name:
                result.append(bid)
        return result

    @classmethod
    def get_task_id_list(cls, cid: str, did: str) -> Dict[str, str]:
        """
        获取任务bid对应任务名称字典
        :param cid:
        :param did:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sql = "SELECT bid, taskName FROM labor_task WHERE cid=%s AND did=%s AND status=1;" % (cid, did)
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            infoLog.info('success: %s' % sql)
        except Exception:
            infoLog.info('falid: %s' % sql)
            res = []
        conn.close()

        result = {}
        for task in res:
            bid = task[0]
            task_name = task[1]
            result[bid] = task_name
        return result

    @classmethod
    def get_task_info(cls, cid: str, did: str, date: str, mode: int = 0) -> Tuple[List[Tuple[str, str, str, str]],
                                                                                  List[Tuple[str, str, str, str]],
                                                                                  List[Tuple[str, int]]]:
        """
        获取任务信息
        :param mode: 0 取value 1 取min 2 取 max
        :param cid:
        :param did:
        :param date:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        if mode == 0:
            sql = "SELECT a.taskBid, a.startTimeStr, a.endTimeStr, a.whour, b.taskType FROM (" \
                  "SELECT dayStr, taskBid, startTimeStr, endTimeStr, SUM(if(editValue!=0, editValue, caclValue)) " \
                  "AS whour FROM labor_cacl_value WHERE dayStr='%s' AND status=1 AND cid=%s AND did=%s AND " \
                  "startTimeStr >='08:00' GROUP BY dayStr, taskBid, startTimeStr, endTimeStr) a LEFT JOIN " \
                  "(SELECT bid, taskType FROM labor_task WHERE status=1) b ON b.bid = a.taskBid " \
                  "ORDER BY a.taskBid" % (date, cid, did)
        elif mode == 1:
            sql = "SELECT a.taskBid, a.startTimeStr, a.endTimeStr, a.min_caclValue, b.taskType FROM (" \
                  "SELECT dayStr, taskBid, startTimeStr, endTimeStr, min_caclValue FROM labor_cacl_value WHERE " \
                  "dayStr='%s' AND status=1 AND cid=%s AND did=%s AND startTimeStr >='08:00') a LEFT JOIN (SELECT " \
                  "bid, taskType FROM labor_task WHERE status=1) b ON b.bid = a.taskBid ORDER BY " \
                  "a.taskBid" % (date, cid, did, bid)
        else:
            sql = "SELECT a.taskBid, a.startTimeStr, a.endTimeStr, a.max_caclValue, b.taskType FROM (SELECT dayStr, " \
                  "taskBid, startTimeStr, endTimeStr, max_caclValue FROM labor_cacl_value WHERE dayStr='%s' AND " \
                  "status=1 AND cid=%s AND did=%s AND startTimeStr >='08:00') a LEFT JOIN (SELECT bid, taskType " \
                  "FROM labor_task WHERE status=1) b ON b.bid = a.taskBid ORDER BY a.taskBid" % (date, cid, did)
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            infoLog.info('success: %s' % sql)
        except Exception:
            infoLog.info('falid: %s' % sql)
            res = []
        conn.close()

        fix_task = []
        direct_task = []
        indirect_task = []
        if res:
            for item in res:
                bid = item[0]
                start_time = item[1]
                end_time = item[2]
                work_time = str(int(item[3]))
                task_type = str(item[4]).strip().lower()
                if not task_type:
                    # 没有taskType
                    continue
                if int(item[3]) <= 0:
                    # 没有工时数据
                    continue
                if task_type == 'directwh':
                    direct_task.append((bid, start_time, end_time, work_time))
                elif task_type == 'indirectwh':
                    indirect_task.append((bid, int(work_time)))
                elif task_type == 'fixedwh':
                    fix_task.append((bid, start_time, end_time, work_time))
                else:
                    # task type不正确
                    continue
        return fix_task, direct_task, indirect_task

    @classmethod
    def get_data(self, cid: str, did: str, start_date: str, end_date: str, bid: str, method):
        """
        by lyy 2020-04-09 两种取数据库方式，1、直接在数据库里处理 2、取出数据再处理
        :param cid:
        :param did:
        :param start_date:
        :param end_date:
        :param bid:
        :param method:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()

        if method == 1:
            sql = "SELECT a.taskBid, a.startTimeStr, a.endTimeStr, a.dayStr, a.whour, a.min_caclValue, a.max_caclValue, " \
                  "b.taskType FROM (SELECT dayStr, taskBid, startTimeStr, endTimeStr, sum(if(editValue!=0, editValue, " \
                  "caclValue)) as whour, sum(min_caclValue) as min_caclValue, sum(max_caclValue) as max_caclValue FROM " \
                  "labor_cacl_value WHERE dayStr>='%s' AND dayStr<='%s' AND status=1 AND cid=%s AND forecastType=%s  AND " \
                  "did=%s GROUP BY dayStr, taskBid, startTimeStr, endTimeStr) a LEFT JOIN " \
                  "( SELECT bid, taskType FROM labor_task WHERE status=1 AND cid=%s AND did=%s) b ON b.bid = a.taskBid " \
                  "WHERE whour>0 AND taskType IS NOT NULL ORDER BY a.taskBid;" % (start_date, end_date, cid, bid, did,
                                                                                  cid, did)
            try:
                cursor.execute(sql)
                res = cursor.fetchall()
                res = pd.DataFrame(res)
            except:
                res = []
            conn.close()
            return res, []
        else:
            sql1 = "SELECT dayStr, taskBid, startTimeStr, endTimeStr, editValue,caclValue,min_caclValue,max_caclValue " \
                   "FROM labor_cacl_value WHERE cid=%s AND did=%s AND forecastType=%s AND dayStr>=%s AND dayStr<=%s AND status=1;"

            try:
                cursor.execute(sql1, (cid, did, bid, start_date, end_date))
                res1 = cursor.fetchall()
                res1 = pd.DataFrame(res1, columns=['dayStr', 'taskBid', 'startTimeStr', 'endTimeStr', 'editValue',
                                                   'caclValue', 'min_caclValue', 'max_caclValue'])
                infoLog.info('success: %s' % sql1)
            except Exception:
                infoLog.info('falid: %s' % sql1)
                res1 = []

            sql2 = "SELECT bid, taskType FROM labor_task WHERE status=1 AND cid=%s AND did=%s;"
            try:
                cursor.execute(sql2, (cid, did))
                res2 = cursor.fetchall()
                res2 = pd.DataFrame(res2, columns=['taskBid', 'taskType'])
                # infoLog.info('success: %s' % sql)
            except Exception:
                # infoLog.info('falid: %s' % sql)
                res2 = []
            conn.close()
            return res1, res2

    @classmethod
    def data_handle(cls, res1, res2, method):
        """
        by lyy 2020-04-09
        method !=1 表示只取出数据，需要进行数据处理，否则不需要处理
        :param res1:
        :param res2:
        :param method:
        :return:
        """
        if len(res1) != 0 and len(res1) != 0 and (method != 1):
            # editValue=0时，将对应的caclValue值赋给editValue
            res1.loc[res1.editValue == 0, 'editValue'] = res1['caclValue']
            # print('++++=newres1====')
            res1 = res1.drop('caclValue', axis=1)
            # print(res1)
            # 将数据按dayStr, taskBid, startTimeStr, endTimeStr分组对editValue求和,并将分组的列还原为df中的列
            res1 = res1.groupby(by=['dayStr', 'taskBid', 'startTimeStr', 'endTimeStr']).agg(
                {'editValue': sum, 'min_caclValue': sum, 'max_caclValue': sum})
            res1 = res1.reset_index()
            # 根据特定值筛选行数据
            res2 = res2[res2['taskBid'].isin(res1['taskBid'])]
            # 合并两个表数据,将第二个表的type数据合并到第一个表中,相当于mysql的left join功能
            new_df = pd.merge(res1, res2, how='left')
            new_df = new_df.drop_duplicates(keep='first')  # 去除重复行，保留第一个
            new_df = new_df.reset_index(drop=True)
            # 删除editValue中为0的值
            new_df = new_df[new_df['editValue'] != 0]
            new_df.dropna(subset=['taskType'], inplace=True)
            new_df = new_df.reset_index(drop=True)
            res = new_df.values.tolist()
        else:
            res = res1
        return res

    @classmethod
    def get_task_info_by_peroid(cls, cid: str, did: str, start_date: str, end_date: str, bid: str) -> \
            Tuple[Dict[str, List[Tuple[str, str, str, str]]], Dict[str, List[Tuple[str, str, str, str]]],
                  Dict[str, List[Tuple[str, int]]], Dict[str, List[Tuple[str, str, str, str]]],
                  Dict[str, List[Tuple[str, str, str, str]]], Dict[str, List[Tuple[str, int]]],
                  Dict[str, List[Tuple[str, str, str, str]]], Dict[str, List[Tuple[str, str, str, str]]],
                  Dict[str, List[Tuple[str, int]]]]:
        """
        获取任务信息 优化 只读取一次
        :param cid:
        :param did:
        :param start_date:
        :param end_date:
        :param bid:
        :return:
        """
        # method:1表示在数据库里处理数据，非1表示只取出数据，不做处理
        method = 2
        res1, res2 = ManPowerForecastDB.get_data(cid, did, start_date, end_date, bid, method)
        res = ManPowerForecastDB.data_handle(res1, res2, method)

        fix_task_dict: Dict[str, List[Tuple[str, str, str, str]]] = {}
        direct_task_dict: Dict[str, List[Tuple[str, str, str, str]]] = {}
        indirect_task_dict: Dict[str, List[Tuple[str, int]]] = {}
        min_fix_task_dict: Dict[str, List[Tuple[str, str, str, str]]] = {}
        min_direct_task_dict: Dict[str, List[Tuple[str, str, str, str]]] = {}
        min_indirect_task_dict: Dict[str, List[Tuple[str, int]]] = {}
        max_fix_task_dict: Dict[str, List[Tuple[str, str, str, str]]] = {}
        max_direct_task_dict: Dict[str, List[Tuple[str, str, str, str]]] = {}
        max_indirect_task_dict: Dict[str, List[Tuple[str, int]]] = {}
        if res:
            for item in res:
                bid = item[0]
                start_time = item[1]
                end_time = item[2]
                day_str = item[3]
                work_time = str(int(item[4] if item[4] else 0))
                min_work_time = str(int(item[5] if item[5] else 0))
                max_work_time = str(int(item[6] if item[6] else 0))
                task_type = str(item[7]).strip().lower()
                if not task_type:
                    # 没有taskType
                    continue
                if int(work_time) <= 0 or int(min_work_time) <= 0 or int(max_work_time) <= 0:
                    # 没有工时数据
                    continue

                if task_type == 'directwh':
                    # 直接
                    direct_task = direct_task_dict.get(day_str, [])
                    direct_task.append((bid, start_time, end_time, work_time))
                    direct_task_dict[day_str] = direct_task

                    min_direct_task = min_direct_task_dict.get(day_str, [])
                    min_direct_task.append((bid, start_time, end_time, min_work_time))
                    min_direct_task_dict[day_str] = min_direct_task

                    max_direct_task = max_direct_task_dict.get(day_str, [])
                    max_direct_task.append((bid, start_time, end_time, max_work_time))
                    max_direct_task_dict[day_str] = max_direct_task

                elif task_type == 'indirectwh':
                    # 间接
                    indirect_task = indirect_task_dict.get(day_str, [])
                    indirect_task.append((bid, int(work_time)))
                    indirect_task_dict[day_str] = indirect_task

                    min_indirect_task = min_indirect_task_dict.get(day_str, [])
                    min_indirect_task.append((bid, int(min_work_time)))
                    min_indirect_task_dict[day_str] = min_indirect_task

                    max_indirect_task = max_indirect_task_dict.get(day_str, [])
                    max_indirect_task.append((bid, int(max_work_time)))
                    max_indirect_task_dict[day_str] = max_indirect_task

                elif task_type == 'fixedwh':
                    # 固定
                    fix_task = fix_task_dict.get(day_str, [])
                    fix_task.append((bid, start_time, end_time, work_time))
                    fix_task_dict[day_str] = fix_task

                    min_fix_task = min_fix_task_dict.get(day_str, [])
                    min_fix_task.append((bid, start_time, end_time, min_work_time))
                    min_fix_task_dict[day_str] = min_fix_task

                    max_fix_task = max_fix_task_dict.get(day_str, [])
                    max_fix_task.append((bid, start_time, end_time, max_work_time))
                    max_fix_task_dict[day_str] = max_fix_task
                else:
                    # task type不正确
                    infoLog.warning('get wrong task type: %s while getting task info.', task_type)
                    continue

        return fix_task_dict, direct_task_dict, indirect_task_dict, min_fix_task_dict, min_direct_task_dict, \
               min_indirect_task_dict, max_fix_task_dict, max_direct_task_dict, max_indirect_task_dict

    @classmethod
    def get_max_shift_length_from_sch_compliance(cls, cid: str, date_str: str) -> int:
        """
        在合规性数据库中获取最大允许的班次时长
        :param cid:
        :param date_str:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()

        sql = "SELECT ruleCpNum, ruleCpType FROM sch_compliance WHERE cid=%s AND status=1 AND caution=\'forbid\' AND " \
              "cycle=\'day\' AND startDate<=\'%s\' AND ruleType=\'shiftrule\' AND ruletag=\'shiftLen\';"\
              % (cid, date_str)

        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            infoLog.info('success: %s' % sql)
        except Exception:
            infoLog.info('failed: %s' % sql)
            result = []
        conn.close()

        if result:
            res_num = 24*60
            for item in result:
                rule_cp_num = int(item[0])
                rule_cp_type = item[1]
                if rule_cp_type == 'gt' or rule_cp_type == 'ge':
                    if rule_cp_num < res_num:
                        res_num = rule_cp_num
                        if rule_cp_type == 'ge':
                            res_num -= 15
            if res_num == 24 * 60:
                # 没有合理记录
                res_num = 480
            infoLog.info("获取到的最大班次长度为%s", str(res_num))
            return res_num
        else:
            # 默认480
            infoLog.warning("未获取到的最大班次长度，默认480")
            return 480

    @classmethod
    def get_task_info_by_peroid2(cls, cid: str, did: str, start_date: str, end_date: str, bid: str) -> \
            Tuple[Dict[str, List[FixedTask]], Dict[str, List[DirectTask]], Dict[str, List[InDirectTask]],
                  Dict[str, List[FixedTask]], Dict[str, List[DirectTask]], Dict[str, List[InDirectTask]],
                  Dict[str, List[FixedTask]], Dict[str, List[DirectTask]], Dict[str, List[InDirectTask]]]:
        """
        获取任务信息 优化 只读取一次
        :param cid:
        :param did:
        :param start_date:
        :param end_date:
        :param bid:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()

        new_end_date = DateUtils.nDatesAgo(end_date, -1)

        sql = "SELECT a.taskBid, a.startTimeStr, a.endTimeStr, a.dayStr, a.whour, a.min_caclValue, a.max_caclValue, " \
              "b.taskType, b.fillCoefficient, b.discard, b.taskMinWorkTime, b.taskMaxWorkTime FROM (SELECT dayStr, " \
              "taskBid, startTimeStr, endTimeStr, sum(if(editValue!=0, editValue, " \
              "caclValue)) as whour, sum(min_caclValue) as min_caclValue, sum(max_caclValue) as max_caclValue FROM " \
              "labor_cacl_value WHERE dayStr>='%s' AND dayStr<='%s' AND status=1 AND cid=%s AND forecastType=%s  AND " \
              "did=%s GROUP BY dayStr, taskBid, startTimeStr, endTimeStr) a LEFT JOIN " \
              "( SELECT DISTINCT bid, taskType, fillCoefficient, discard, taskMinWorkTime, taskMaxWorkTime FROM " \
              "labor_task WHERE status=1 AND cid=%s AND did=%s) b ON b.bid = a.taskBid " \
              "WHERE whour>0 AND taskType IS NOT NULL ORDER BY a.taskBid;" % (start_date, new_end_date, cid, bid, did,
                                                                              cid, did)
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            infoLog.info('success: %s' % sql)
        except Exception:
            infoLog.info('failed: %s' % sql)
            res = []
        conn.close()

        fix_task_dict: Dict[str, List[FixedTask]] = {}
        direct_task_dict: Dict[str, List[DirectTask]] = {}
        indirect_task_dict: Dict[str, List[InDirectTask]] = {}
        min_fix_task_dict: Dict[str, List[FixedTask]] = {}
        min_direct_task_dict: Dict[str, List[DirectTask]] = {}
        min_indirect_task_dict: Dict[str, List[InDirectTask]] = {}
        max_fix_task_dict: Dict[str, List[FixedTask]] = {}
        max_direct_task_dict: Dict[str, List[DirectTask]] = {}
        max_indirect_task_dict: Dict[str, List[InDirectTask]] = {}
        if res:
            for item in res:
                bid = item[0]
                start_time = item[1]
                end_time = item[2]
                day_str = item[3]
                work_time = int(item[4] if item[4] else 0)
                min_work_time = int(item[5] if item[5] else 0)
                max_work_time = int(item[6] if item[6] else 0)
                task_type = str(item[7]).strip().lower()
                fill_coef = float(item[8] if item[8] else 0.5)
                if item[9]:
                    if int(item[9]) == 2:
                        discard = False
                    else:
                        discard = True
                else:
                    discard = True

                task_min_work_time = int(item[10] if item[10] else 0)
                task_max_work_time = int(item[11] if item[11] else 480)  # 8 hours

                if task_max_work_time < 30:
                    task_max_work_time = 480

                if not task_type:
                    # 没有taskType
                    continue
                if int(work_time) <= 0 or int(min_work_time) <= 0 or int(max_work_time) <= 0:
                    # 没有工时数据
                    continue

                if end_time <= '06:00' and start_time < '06:00':
                    day_str = DateUtils.nDatesAgo(day_str, 1)
                    if day_str < start_date:
                        continue

                if day_str > end_date:
                    continue

                if task_type == 'directwh':
                    # 直接
                    direct_task = direct_task_dict.get(day_str, [])
                    task = DirectTask(bid, start_time, end_time, work_time, fill_coef, discard, task_min_work_time,
                                      task_max_work_time)
                    direct_task.append(task)
                    direct_task_dict[day_str] = direct_task

                    min_direct_task = min_direct_task_dict.get(day_str, [])
                    min_task = DirectTask(bid, start_time, end_time, min_work_time, fill_coef, discard,
                                          task_min_work_time, task_max_work_time)
                    min_direct_task.append(min_task)
                    min_direct_task_dict[day_str] = min_direct_task

                    max_direct_task = max_direct_task_dict.get(day_str, [])
                    max_task = DirectTask(bid, start_time, end_time, max_work_time, fill_coef, discard,
                                          task_min_work_time, task_max_work_time)
                    max_direct_task.append(max_task)
                    max_direct_task_dict[day_str] = max_direct_task

                elif task_type == 'indirectwh':
                    # 间接
                    indirect_task = indirect_task_dict.get(day_str, [])
                    task = InDirectTask(bid, work_time)
                    indirect_task.append(task)
                    indirect_task_dict[day_str] = indirect_task

                    min_indirect_task = min_indirect_task_dict.get(day_str, [])
                    min_task = InDirectTask(bid, min_work_time)
                    min_indirect_task.append(min_task)
                    min_indirect_task_dict[day_str] = min_indirect_task

                    max_indirect_task = max_indirect_task_dict.get(day_str, [])
                    max_task = InDirectTask(bid, max_work_time)
                    max_indirect_task.append(max_task)
                    max_indirect_task_dict[day_str] = max_indirect_task

                elif task_type == 'fixedwh':
                    # 固定
                    fix_task = fix_task_dict.get(day_str, [])
                    task = FixedTask(bid, start_time, end_time, work_time, fill_coef, discard, task_min_work_time,
                                     task_max_work_time)
                    fix_task.append(task)
                    fix_task_dict[day_str] = fix_task

                    min_fix_task = min_fix_task_dict.get(day_str, [])
                    min_task = FixedTask(bid, start_time, end_time, min_work_time, fill_coef, discard,
                                         task_min_work_time, task_max_work_time)
                    min_fix_task.append(min_task)
                    min_fix_task_dict[day_str] = min_fix_task

                    max_fix_task = max_fix_task_dict.get(day_str, [])
                    max_task = FixedTask(bid, start_time, end_time, max_work_time, fill_coef, discard,
                                         task_min_work_time, task_max_work_time)
                    max_fix_task.append(max_task)
                    max_fix_task_dict[day_str] = max_fix_task
                else:
                    # task type不正确
                    infoLog.warning('get wrong task type: %s while getting task info.', task_type)
                    continue

        return fix_task_dict, direct_task_dict, indirect_task_dict, min_fix_task_dict, min_direct_task_dict, \
               min_indirect_task_dict, max_fix_task_dict, max_direct_task_dict, max_indirect_task_dict

    @classmethod
    def getTaskData(cls, cid, did, bid, forecastStart, forecastEnd):
        """
        连接数据库woqu，获取任务数据，放入表day_taskdata中
        by: lyy 2019-12-10
        """

        flag = 0  # 数据库操作初始状态，默认0代表成功
        # 打开数据库连接
        db = DBPOOL.connection()
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        # print(daystr)
        # cursor.execute("DROP TABLE IF EXISTS day_taskdata")
        # sql1 = "CREATE TABLE day_taskdata(`auto_id` int auto_increment primary key comment '自增主键',dayStr VARCHAR(50),taskBid VARCHAR(50),startTimeStr VARCHAR(50),whour DOUBLE,taskType VARCHAR(50));"

        # 先软删除已存在的数据
        sql_delete = "UPDATE day_taskdata_lyy SET status=0 WHERE dayStr >=%s AND dayStr <= %s;"
        cursor.execute(sql_delete, (forecastStart, forecastEnd))
        db.commit()
        # 初始化sql
        sql = None
        # SQL 查询语句
        sql = "SELECT a.dayStr,a.taskBid,a.startTimeStr,a.whour,a.minhour,a.maxhour, b.taskType,1 FROM (" \
              "SELECT dayStr,taskBid,startTimeStr,sum(if(editValue!=0,editValue,caclValue)) as whour," \
              "sum(min_caclValue) as minhour,sum(max_caclValue) as maxhour FROM labor_cacl_value " \
              "WHERE dayStr >=%s and dayStr <=%s and startTimeStr >='08:00' and cid=%s and did = %s AND forecastType=%s and `status`=1 GROUP BY taskBid,dayStr,startTimeStr) a " \
              "LEFT JOIN (SELECT distinct bid,taskType FROM labor_task  WHERE `status`=1) b  ON b.bid = a.taskBid " \
              "ORDER BY a.taskBid;"

        try:
            cursor.execute(sql, (forecastStart, forecastEnd, cid, did[0], bid))
            # 获取所有记录列表
            results = cursor.fetchall()
            sql_insert = "INSERT INTO day_taskdata_lyy(dayStr,taskBid,startTimeStr,whour,minhour,maxhour,taskType,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
            # 将查到的数据批量插入
            cursor.executemany(sql_insert, results)
            db.commit()
        except Exception:
            db.rollback()
            flag = 1
        # 关闭数据库连接
        db.close()
        return flag

        # while num_start <= num_end:
        #     # 执行SQL语句
        #     cursor.execute(sql, (daystr, starttime, cid, did[0],bid))
        #     # 获取所有记录列表
        #     results = cursor.fetchall()
        #     for row in results:
        #         # 将查到的数据插入表
        #         sql1 = "INSERT INTO day_taskdata VALUES(%s,%s,%s,%s,%s)"
        #         cursor.execute(sql1, (row[0], row[1], row[2], row[3], row[4]))
        #         db.commit()
        #     num_start += 0.5
        #     starttime = numtostr(num_start)  # 当前时间加半小时后的时间

    @classmethod
    def getTaskRecord(cls, daystr, mode):
        """
        by: lyy 2019-12-10
        :return:
        """
        import pandas as pd
        flag = 0  # 数据库操作初始状态，默认0代表成功

        # 打开数据库连接
        db = DBPOOL.connection()
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        jj_task = []  # 所有的间接任务
        zj_df = None
        # 先判断当天有没有任务数据
        exist_flag = 0  # 默认当天有任务数据,2 无数据
        try:
            sql_if_exist = "SELECT * FROM day_taskdata_lyy WHERE dayStr=%s AND status=1;"
            cursor.execute(sql_if_exist, daystr)
            db.commit()
            record = cursor.fetchone()
            if record is None:  # 当天数据不存在
                exist_flag = 2
                # 关闭数据库连接
                db.close()
                return [], [], exist_flag
        except Exception:
            db.rollback()
            flag = 1  # 数据库操作失败

        sql_df = None
        sql_df_ind = None
        if mode == 0:
            # 非间接任务
            sql_df = "SELECT dayStr,taskBid,startTimeStr,whour,taskType FROM day_taskdata_lyy WHERE taskType!='indirectwh' AND status=1 AND dayStr=%s;"
            # 间接任务
            sql_df_ind = "SELECT dayStr,taskBid,sum(whour),taskType FROM day_taskdata_lyy WHERE taskType ='indirectwh' AND status=1 AND dayStr=%s GROUP BY dayStr,taskBid;"
        elif mode == 1:
            # 非间接任务
            sql_df = "SELECT dayStr,taskBid,startTimeStr,minhour,taskType FROM day_taskdata_lyy WHERE taskType!='indirectwh' AND status=1 AND dayStr=%s;"
            # 间接任务
            sql_df_ind = "SELECT dayStr,taskBid,sum(minhour),taskType FROM day_taskdata_lyy WHERE taskType ='indirectwh' AND status=1 AND dayStr=%s GROUP BY dayStr,taskBid;"
        elif mode == 2:
            # 非间接任务
            sql_df = "SELECT dayStr,taskBid,startTimeStr,maxhour,taskType FROM day_taskdata_lyy WHERE taskType!='indirectwh' AND status=1 AND dayStr=%s;"
            # 间接任务
            sql_df_ind = "SELECT dayStr,taskBid,sum(maxhour),taskType FROM day_taskdata_lyy WHERE taskType ='indirectwh' AND status=1 AND dayStr=%s GROUP BY dayStr,taskBid;"

        try:
            cursor.execute(sql_df, daystr)
            db.commit()
            results = cursor.fetchall()

            dayStr = []
            taskBid = []
            startTimeStr = []
            whour = []
            taskType = []
            for res in results:
                dayStr.append(res[0])
                taskBid.append(res[1])
                startTimeStr.append(res[2])
                whour.append(res[3])
                taskType.append(res[4])
            data = {'dayStr': dayStr, 'taskBid': taskBid, 'startTimeStr': startTimeStr, 'whour': whour,
                    'taskType': taskType}
            zj_df = pd.DataFrame(data=data)
        except Exception:
            db.rollback()
            flag = 1

        try:
            cursor.execute(sql_df_ind, daystr)
            results2 = cursor.fetchall()
            jj_task = list(results2)
            # for res in results2:
            #     jj_task.append((res[0], res[1], res[2], res[3]))
        except Exception:
            db.rollback()
            flag = 1

        # 关闭数据库连接
        db.close()
        return zj_df, jj_task, flag  # flag=1,操作数据库失败

    @classmethod
    def insert_result(cls, did_arr, date, cid, bid, combiRule, combiRuleNewVal, combiRuleOldVal, combiRuleCalcVal):
        """
        将排班结果存入数据库
        by lyy 2019-10-09
        :param date:
        :param cid:
        :param bid:
        :return:
        """
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        did = did_arr[0]
        # 先把已有的数据状态置为0，保证以后使用的都是最新数据
        sql1 = "UPDATE labor_man_power SET status=0 AND update_time=%s WHERE cid=%s AND did=%s AND forecastType=%s " \
               "AND forecast_date=%s AND resultMethod=0;"
        try:
            cursor.execute(sql1, (now_datetime, cid, did, bid, date))
            conn.commit()
        except Exception:
            infoLog.warning(
                'FAILED, sql: UPDATE labor_man_power SET status=0 AND update_time=%s WHERE cid=%s AND did=%s AND forecastType=%s AND forecast_date=%s AND resultMethod=0',
                now_datetime, cid, did, bid, date)
            conn.rollback()
            res_flag = False

        sql = "INSERT INTO labor_man_power(cid,forecastType,did,forecast_date,combiRule,combiRuleNewVal,combiRuleOldVal,combiRuleCalcVal,resultMethod,create_time,update_time,status) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            cursor.execute(sql, (
                cid, bid, did, date, combiRule, combiRuleNewVal, combiRuleOldVal, combiRuleCalcVal, 0, now_datetime,
                now_datetime, 1))
            conn.commit()
        except Exception:
            conn.rollback()
            res_flag = False

        conn.close()
        return res_flag

    @classmethod
    # 将排好的任务矩阵存入数据库表task_matrix_lyy
    def insert_matrix(cls, date, cid, did, task_matrix, id_li, split_rule, indirect_task, bid, mode):
        """
        by lyy 2019-10-21
        """
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        task_matrix = json.dumps(task_matrix)  # 将列表转化为json格式
        id_li = json.dumps(id_li)  # 将列表转化为json格式
        split_rule = json.dumps(split_rule)  # 将字典转化为json格式
        indirect_task = json.dumps(indirect_task)
        # 先把已有的数据状态置为0，保证以后使用的都是最新数据
        sql1 = "UPDATE task_matrix_lyy SET status=0 AND update_time=%s WHERE cid=%s AND did=%s AND forecast_date=%s AND forecastType=%s AND data_type=%s AND status=1;"
        try:
            cursor.execute(sql1, (now_datetime, cid, did, date, bid, str(mode)))
            conn.commit()
        except Exception:
            infoLog.warning(
                'FAILED, sql: UPDATE task_matrix_lyy SET status=0 AND update_time=%s WHERE cid=%s AND did=%s AND forecast_date=%s AND forecastType=%s AND data_type=%s AND status=1;',
                now_datetime, cid, did, date, bid, str(mode))
            conn.rollback()
            res_flag = False

        sql2 = "INSERT INTO task_matrix_lyy(cid,did,forecastType,forecast_date,task_matrix,create_time,update_time,status,id_li,split_rule,indirect_task,data_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            cursor.execute(sql2, (
                cid, did, bid, date, task_matrix, now_datetime, now_datetime, 1, id_li, split_rule, indirect_task,
                str(mode)))
            conn.commit()
        except Exception:
            infoLog.warning(
                'FAILED, sql: INSERT INTO task_matrix_lyy(cid,did,forecast_date,task_matrix,create_time,update_time,status,id_li,split_rule,indirect_task,data_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',
                cid, did, bid, date, task_matrix, now_datetime, now_datetime, 1, id_li, split_rule, indirect_task,
                str(mode))
            conn.rollback()
            res_flag = False

        conn.close()
        return res_flag

    @classmethod
    # 将排好的任务矩阵存入数据库表task_matrix_ss
    def insert_matrix_ss(cls, cid: str, did: str, forecastType: str, type: str, forecast_date: str, startTime,
                         endTime: str,
                         task_matrix: List):
        """
        by liyabin 2019-11-5
        """
        res_flag = True
        now_datetime = DateUtils.get_now_datetime_str()
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        task_matrix = json.dumps(task_matrix)  # 将列表转化为json格式
        # 先把已有的数据状态置为0，保证以后使用的都是最新数据
        sql1 = "UPDATE task_matrix_ss SET status=0 AND update_time=%s WHERE cid=%s AND did=%s AND forecastType=%s AND `type`=%s AND forecast_date=%s"
        # sql1 = "DELETE FROM task_matrix_ss  WHERE cid=%s AND did=%s AND type=%s AND forecast_date=%s;"

        try:
            cursor.execute(sql1, (now_datetime, cid, did, forecastType, type, forecast_date))
            conn.commit()
        except Exception:
            infoLog.warning('FAILED, sql: %s' % sql1)
            conn.rollback()
            res_flag = False

        sql2 = "INSERT INTO task_matrix_ss(cid,did,forecastType,`type`,forecast_date,start_time,end_time,task_matrix,update_time,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        try:
            cursor.execute(sql2, (
            cid, did, forecastType, type, forecast_date, startTime, endTime, task_matrix, now_datetime, 1))
            conn.commit()
        except Exception:
            infoLog.warning('FAILED, sql: %s' % sql2)
            conn.rollback()
            res_flag = False

        conn.close()
        return res_flag

    @classmethod
    def get_matrix_info(cls, cid: str, did: str, forecast_type: str, date: str) -> Tuple[str, str, List[List[str]]]:
        """
        获取信息
        :param cid:
        :param did:
        :param forecast_type:
        :param date:
        :return:
        """
        conn = DBPOOL.connection()
        cursor = conn.cursor()
        sql = 'SELECT start_time, end_time, task_matrix FROM task_matrix_ss WHERE cid=\'%s\' AND did=\'%s\' AND ' \
              'forecastType=\'%s\' AND forecast_date=\'%s\' AND status=1 AND type=\'full\';'
        try:
            cursor.execute(sql % (cid, did, forecast_type, date))
            result = cursor.fetchall()
        except Exception:
            infoLog.warning('FAILED, sql: %s', sql)
            result = []
        # conn.close()

        if len(result) != 0:
            start_time = result[0][0]
            end_time = result[0][1]
            task_matrix_str = result[0][2]
            task_matrix = json.loads(task_matrix_str)
            return start_time, end_time, task_matrix
        else:
            return '', '', []


if __name__ == '__main__':
    # ManPowerForecastDB.insert_matrix_ss(cid='123456',did='6',forecastType='1',type='full',forecast_date='2019-07-12',startTime='05:30',endTime='13:00',task_matrix=[[1,2,3],[4,5,6]])
    res = ManPowerForecastDB.get_matrix_info('50000031', '7692', '2', '2019-07-10')
    print(res)
