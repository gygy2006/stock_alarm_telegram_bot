import requests
import xlrd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from api import my_header

KRX_HOLIDAY_URL = "http://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp"


def today():
    return datetime.today()


def year():
    return datetime.today().year


def weekday(day):
    return day.weekday()


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


# 현재일자 부터 5일 전 까지 공휴일 , 주말 구분하여 카운팅해줌
def count_holiday():
    day_calculator = []
    holidays = stock_holiday()
    for i in range(5):  # range 값을 바꿔서 일자 조절가능
        day = today() + timedelta(days=-i)  # format : datetime
        if str(day)[:10] in holidays:  # format: yyyy-mm-dd
            day_calculator.append(False)
        elif weekday(day) > 4:
            day_calculator.append(False)
        else:
            day_calculator.append(True)
    weekday_number_of_time = day_calculator.count(False)
    if weekday(day) == 6:
        weekday_number_of_time += 1
    return weekday_number_of_time
