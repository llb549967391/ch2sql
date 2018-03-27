# -*- coding: utf-8 -*-
"""

Author: Rob

contributor:

This is a script file processing string about date.

version1.0:这个版本目前只支持阿拉伯数字

version2.0:增加了同义词识别功能
		   增加了周为单位日期的识别功能


"""
from datetime import date
from ch2sql.tools import synonyms as sym
import datetime
import calendar


# 获取当前季度

# 将字符日期转换为数字日期
def ch2date(str_in):
    # 记录返回结果是否按月
    byMon = False

    # 记录返回结果是否按年
    byYear = False

    # return a time object including today's date to variable today
    today = date.today()

    #记录今天是星期几
    week_day = int(today.strftime('%w'))

    # 记录终止日期，默认中止日期为当前日期
    end = today

    # initialise beginning date, default to be today
    begin = today

    #同义词阈值
    threshold = 0.6

    # judge the query date type, if isRange equals True, ignore 'end',
    # else both are valid
    isRange = False

    # 预处理
    str_in = str_in.strip()

    if (str_in.find('每月') != -1) | (str_in.find('每个月') != -1):
        byMon = True
        str_in = str_in.replace('每月', '')
        str_in = str_in.replace('每个月', '')

    if (str_in.find('每年') != -1) | (str_in.find('每一年') != -1):
        byYear = True
        str_in = str_in.replace('每年', '')
        str_in = str_in.replace('每一年', '')

    # 根据自然语言进行对应的处理
    # 特殊情况处理
    if str_in == '':
        return begin, end, isRange, byMon, byYear

    elif sym.compare(str_in, '昨天') >= threshold:
        begin = today - datetime.timedelta(1)

    elif sym.compare(str_in, '前天') >= threshold:
        begin = today - datetime.timedelta(2)

    elif str_in.find('天前') != -1:
        days = int(str_in[0:str_in.find('天前')])
        begin = today - datetime.timedelta(days)


    # 最近类型日期处理
    elif str_in.find('最近') != -1:
        isRange = True

        str_begin = str_in.find('最近') + 2

        str_in = str_in[str_begin:]

        t_split = sym.seg(str_in)[0]

        number = int(t_split[0])

        cha = t_split[-1]

        if sym.compare(cha, '年') >= threshold:
            year = today.year - number
            begin = begin.replace(year, 1, 1)

        if sym.compare(cha, '季度') >= threshold:
            season = (today.month - 1) // 3 - number
            year = today.year
            month = season * 3 + 1
            while month < 0:
                year -= 1
                month += 12

            begin = begin.replace(year, month, 1)

        if sym.compare(cha, '月') >= threshold:
            year = today.year
            month = today.month - number
            while month < 0:
                year -= 1
                month += 12
            begin = begin.replace(year, month, 1)

        if (sym.compare(cha, '周') >= threshold) | (sym.compare(cha, '礼拜') >= threshold):
            begin = today - datetime.timedelta(number * 7 + week_day)

        if sym.compare(cha, '天') >= threshold:
            begin = today - datetime.timedelta(number)



    # 年月日类型日期处理
    elif str_in.find('年') != -1:

        isRange = True

        year_loc = str_in.find('年') + 1

        year_part = str_in[0:year_loc]

        # 年的特殊情况处理
        if (sym.compare(year_part, '今年') >= threshold) | (str_in.find('该年') != -1) | (str_in.find('这一年')):
            year = today.year

        elif sym.compare(year_part, '去年') >= threshold:
            year = today.year - 1

        elif sym.compare(year_part, '前年') >= threshold:
            year = today.year - 2

        # 年的通用情况处理
        else:
            year = int(str_in[0:year_loc - 1])

        if str_in.find('月') == -1:

            begin = today.replace(year, 1, 1)
            if year != today.year:
                end = today.replace(year, 12, 31)

        else:

            month_loc = str_in.find('月') + 1
            month = int(str_in[year_loc : (month_loc - 1)])

            if (str_in.find('日') == -1) & (str_in.find('号') == -1):

                day = calendar.monthrange(year, month)[1]

                begin = today.replace(year, month, 1)
                end = today.replace(year, month, day)

            else:

                if str_in.find('日') != -1:
                    day = int(str_in[month_loc: str_in.find('日')])
                elif str_in.find('号') != -1:
                    day = int(str_in[month_loc: str_in.find('号')])

                isRange = False
                begin = begin.replace(year, month, day)

                # 没有年的特殊情况处理
    elif (str_in.find('这') != -1) | (str_in.find('本') != -1):

        isRange = True

        if str_in.find('月') != -1:
            year = today.year
            month = today.month

            begin = begin.replace(year, month, 1)

        if str_in.find('季度') != -1:
            season = (today.month - 1) // 3
            year = today.year
            month = season * 3 + 1

            begin = begin.replace(year, month, 1)

        if (str_in.find('周') != -1) | (str_in.find('星期') != -1) | (str_in.find('礼拜') != -1):
            begin = today - datetime.timedelta(week_day)


    elif str_in.find('上') != -1:

        isRange = True

        if str_in.find('月') != -1:

            year = today.year
            month = today.month - 1

            while month < 0:
                year -= 1
                month += 12

            day = calendar.monthrange(year, month)[1]

            begin = begin.replace(year, month, 1)
            end = end.replace(year, month, day)

        if str_in.find('季度') != -1:
            season = (today.month - 1) // 3 - 1
            year = today.year
            month = season * 3 + 1
            while month < 0:
                year -= 1
                month += 12

            begin = begin.replace(year, month, 1)

            month += 2
            while month > 12:
                year += 1
                month -= 12

            day = calendar.monthrange(year, month)[1]

            end = end.replace(year, month, day)

        if (str_in.find('周') != -1) | (str_in.find('星期') != -1) | (str_in.find('礼拜') != -1):
            begin = today - datetime.timedelta(7 + week_day)
            end = today - datetime.timedelta(week_day)


    elif str_in.find('前') != -1:
        isRange = True

        if str_in.find('月') != -1:
            year = today.year
            month = today.month - 2
            while month < 0:
                year -= 1
                month += 12

            day = calendar.monthrange(year, month)[1]

            begin = begin.replace(year, month, 1)
            end = end.replace(year, month, day)

        if str_in.find('季度') != -1:
            season = (today.month - 1) // 3 - 2
            year = today.year
            month = season * 3 + 1
            while month < 0:
                year -= 1
                month += 12

            begin = begin.replace(year, month, 1)

            month += 2
            while month > 12:
                year += 1
                month -= 12

            day = calendar.monthrange(year, month)[1]

            end = end.replace(year, month, day)

        if (str_in.find('周') != -1) | (str_in.find('星期') != -1) | (str_in.find('礼拜') != -1):
            begin = today - datetime.timedelta(14 + week_day)
            end = today - datetime.timedelta(7 + week_day)

    # 没有年的情况处理
    elif str_in.find('月') != -1:

        isRange = True

        year = today.year
        month = int(str_in[0:str_in.find('月')])
        day = calendar.monthrange(year, month)[1]

        begin = today.replace(year, month, 1)
        end = today.replace(year, month, day)


    # 没有月的情况处理
    elif (str_in.find('日') != -1) | (str_in.find('号') != -1):

        isRange = False

        year = today.year
        month = today.month

        if str_in.find('日') != -1:
            day = int(str_in[0:str_in.find('日')])

        elif str_in.find('号') != -1:
            day = int(str_in[0:str_in.find('号')])

        begin = begin.replace(year, month, day)

    return begin, end, isRange, byMon, byYear


#测试模块
if __name__ == '__main__':
    str_in = '前'

    begin, end, isRange, byMon, byYear = ch2date(str_in)

    print(begin)
    print(end)
    print(isRange)
    print(byMon)
    print(byYear)
