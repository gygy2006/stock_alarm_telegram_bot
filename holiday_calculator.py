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


def today():
    return datetime.today()


def year():
    return datetime.today().year


def date_conversion(date):
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
    date = date_conversion(date)
    if date.weekday() > 4 or stock_closed_day_is_valid(date):
        return True


def stock_closed_day_is_valid(date):
    holidays = stock_holiday()
    if str(date)[:10] in holidays:
        return True


def next_day(date):
    date = date_conversion(date) + timedelta(days=1)
    while holiday_is_valid(date):
        date += timedelta(days=1)
    return date


# 현재일자 부터 5일 전 까지 공휴일 , 주말 구분하여 카운팅해줌
def count_holiday():
    day_calculator = []
    holidays = stock_holiday()
    for i in range(5):  # range 값을 바꿔서 일자 조절가능
        day = today() + timedelta(days=-i)  # format : datetime
        if holiday_is_valid(day):
            day_calculator.append(True)
        else:
            day_calculator.append(False)
    weekday_number_of_time = day_calculator.count(True)
    if day.weekday() == 6:  # for 문 마지막 요일이 일요일 이었을 경우
        weekday_number_of_time += 1

    return weekday_number_of_time
