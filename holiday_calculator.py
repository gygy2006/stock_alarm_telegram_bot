import requests
import xlrd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from api import my_header

KRX_HOLIDAY_URL = "http://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp"


# 공휴일을 받아옴
def stock_holiday():
    holidays = []
    for i in range(-1, 2):
        holiday_excel = xlrd.open_workbook(f"./holiday/{year()+i}.xls")
        worksheet = holiday_excel.sheet_by_index(0)
        rows = worksheet.nrows  # 행
        holiday = worksheet.col_values(0, 1, rows)
        holidays += holiday
    return holidays


def year():
    return datetime.today().year


def is_datetime_conversion(date):
    if not isinstance(date, datetime):
        year = date[:4]
        month = date[4:6]
        day = date[6:]
        if month[0] == "0":
            month = date[5]
        if day[0] == "0":
            day = day[-1]
        date = datetime(int(year), int(month), int(day))
    return date


def holiday_is_valid(date):
    date = is_datetime_conversion(date)
    if date.weekday() > 4 or stock_closed_day_is_valid(date):
        return True


def stock_closed_day_is_valid(date):
    holidays = stock_holiday()
    if str(date)[:10] in holidays:
        return True


def next_day(date):
    date = is_datetime_conversion(date) + timedelta(days=1)
    while holiday_is_valid(date):  # 다음날이 휴장일일경우 휴장일이 아닌 미래의 날을 next day 로 지정
        date += timedelta(days=1)
    return date


def stock_today(date):
    date = is_datetime_conversion(date)
    while holiday_is_valid(date):
        date += timedelta(days=-1)
    return date


def recent_data_is_valid():
    today = datetime.today()
    if holiday_is_valid(today):
        result = stock_today(today)
        return result
    return False


# 전,후 일자 부터 지정일 전후 까지 공휴일 , 주말 구분하여 카운팅해줌
def count_holiday(date, range_day, down_range=True):
    date = is_datetime_conversion(date)
    day_calculator = []
    holidays = stock_holiday()
    for i in range(1, range_day + 1):  # range 값을 바꿔서 일자 조절가능
        if down_range:
            day = date + timedelta(days=-i)  # format : datetime
        else:
            day = date + timedelta(days=i)
            # print(f"{date} + {i} = {day}")
        if holiday_is_valid(day):
            day_calculator.append(True)
        else:
            day_calculator.append(False)
    weekday_number_of_time = day_calculator.count(True)
    if down_range:
        if day.weekday() == 6:  # for 문 마지막 요일이 일요일 이었을 경우
            weekday_number_of_time += 1

    return weekday_number_of_time
