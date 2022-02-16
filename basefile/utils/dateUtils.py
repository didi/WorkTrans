import datetime
from typing import List, Tuple
from utils.task import FixedTask, DirectTask

import sys

sys.setrecursionlimit(9000000)

# 私有方法 禁用
def getStr(minute: int):
    if minute == 0:
        return "00"
    elif minute > 0 and minute < 10:
        return "0" + str(minute)
    else:
        return str(minute)

# 私有方法 禁用
def getTimeArr(_start, _end, min, listDate: List[str]):
    listDate.append(getStr(_start.hour) + ":" + getStr(_start.minute))
    if _start >= _end:
        return listDate
    _start = _start + datetime.timedelta(minutes=min)
    getTimeArr(_start, _end, min, listDate)

class DateUtils:

    @staticmethod
    def nDatesAgo(baseDay, n):
        """
        获取当前日期几天前的日期
        :param n: 几天前
        :return: 日期
        """

        result_date = datetime.datetime.strptime(baseDay, '%Y-%m-%d') - datetime.timedelta(days=n)
        nDay = result_date.strftime('%Y-%m-%d')

        return nDay

    @staticmethod
    def get_yesterday_date_str() -> str:
        """
        获取当前日期前一天的日期字符串
        :return:
        """
        now_time = datetime.datetime.now()
        yesterday = now_time - datetime.timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')

    @staticmethod
    def get_now_datetime_str() -> str:
        """
        获取当前的datetime字符串
        :return:
        """
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_date_array(start_date_str: str, end_date_str: str, fmt: str = '%Y-%m-%d') -> List[str]:
        """
        获取从start date 到 end date 的string list
        :param start_date_str:
        :param end_date_str:
        :param fmt:
        :return:
        """
        start_date = datetime.datetime.strptime(start_date_str, fmt)
        end_date = datetime.datetime.strptime(end_date_str, fmt)

        result: List[str] = []

        while start_date <= end_date:
            result.append(start_date.strftime(fmt))
            start_date = start_date + datetime.timedelta(days=1)

        return result

    @staticmethod
    def get_start_time_and_end_time(fixed_tasks: List[FixedTask],
                                    direct_tasks: List[DirectTask],
                                    is_cross_day: bool = False) -> Tuple[str, str]:
        """
        获得start time和end time
        :param is_cross_day:
        :param fixed_tasks:
        :param direct_tasks:
        :return:
        """
        # 临时规则：
        # 只要有结束时间出现在0-6点就算跨天
        # 否则都不是跨天
        is_cross_day = False
        for item in fixed_tasks + direct_tasks:
            if '00:00' <= item.end_time <= '06:00':
                is_cross_day = True
                break
        if not is_cross_day:
            start_time = '23:59'
            end_time = '00:00'
            for item in fixed_tasks + direct_tasks:
                if item.start_time < start_time:
                    start_time = item.start_time
                if item.end_time > end_time:
                    end_time = item.end_time
            return start_time, end_time
        else:
            temp_split = '06:00'
            start_time = '23:59'
            end_time = '00:00'
            for item in fixed_tasks + direct_tasks:
                if temp_split < item.start_time < start_time:
                    start_time = item.start_time
                if end_time < item.end_time <= temp_split:
                    end_time = item.end_time
            return start_time, end_time

    @staticmethod
    def get_new_time_15_minute(time: str) -> Tuple[int, int]:
        """
        :rtype: object
        :param time: %H:%M:%S 字符串
        :return: [小时， 分钟]
        """
        try:
            _time = datetime.datetime.strptime(time, "%H:%M:%S")
        except Exception as e:
            return None
        hour = _time.hour
        minute = _time.minute
        second = _time.second
        if minute == 0:
            minute = 0
        else:
            s = int(minute / 15)
            if minute % 15 == 0 and second == 0:
                s = s - 1
            minute = s * 15
        if minute == 60:
            hour = hour + 1
            minute = 0
        return hour, minute

    @staticmethod
    def get_new_time_60_minute(time: str) -> Tuple[int, int]:
        """
        :rtype: object
        :param time: yyyy-MM-dd 字符串
        :return: [小时， 分钟]
        """
        try:
            _time = datetime.datetime.strptime(time, "%H:%M:%S")
        except Exception as e:
            return None
        hour = _time.hour
        # 60 分钟 都是整点

        return hour, 0

    @staticmethod
    def get_start_end_min_array(start: str, end: str, min: int):
        form = "%H:%M"
        _start = DateUtils.transTime(start, form)
        _end = DateUtils.transTime(end, form)
        if _start is None or _end is None:
            return None
        if min < 1:
            return None
        listDate = []
        # 处理跨天的情况
        if _start >= _end:
            _end = _end + datetime.timedelta(days=1)
        getTimeArr(_start, _end, min, listDate)
        return listDate

    @staticmethod
    def transTime(date_str, format):
        try:
            result = datetime.datetime.strptime(date_str, format)
            return result
        except Exception:
            return None

    @staticmethod
    def trfHourAndMin(hourOrMin):
        if hourOrMin < 9:
            return "0" + str(hourOrMin)
        return str(hourOrMin)


class Date2delta:
    def __init__(self,):
        pass

    def day2delta(self,date):
        return datetime.timedelta(days=date)

    def minute2delta(self,date):
        return datetime.timedelta(minutes=date)

    def hour2delta(self,date):
        return datetime.timedelta(hours=date)

    def time_delta(self,time_type,date):
        if time_type=="D":
            return self.day2delta(date)
        elif time_type=="H":
            return self.hour2delta(date)
        elif time_type=="T":
            return self.minute2delta(date)



if __name__ == '__main__':
    print(DateUtils.nDatesAgo('2019-07-15',9))