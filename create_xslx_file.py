import pymysql
import pandas as pd
import time
import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from datetime import datetime, timedelta
from holiday_calculator import is_datetime_conversion, holiday_is_valid, next_day
from stock_data import Kiwoom
from openpyxl import load_workbook


today = datetime(2020, 10, 14).strftime("%Y%m%d")
# today = datetime.today().strftime("%Y%m%d")
excel_row = 1
data_box = []
cleaned_data = []

db = pymysql.connect(
    host="localhost",
    user="root",
    password="As731585!",
    db="foreign_ins_purchases",
    charset="utf8mb4",
)

cur = db.cursor()
db.commit()
app = QApplication(sys.argv)
kiwoom = Kiwoom()
kiwoom.comm_connect()


def append_df_to_excel(
    filename,
    df,
    sheet_name="Sheet1",
    startrow=None,
    truncate_sheet=False,
    **to_excel_kwargs,
):
    """
    Append a DataFrame [df] to existing Excel file [filename]
    into [sheet_name] Sheet.
    If [filename] doesn"t exist, then this function will create it.

    Parameters:
      filename : File path or existing ExcelWriter
                 (Example: "/path/to/file.xlsx")
      df : dataframe to save to workbook
      sheet_name : Name of sheet which will contain DataFrame.
                   (default: "Sheet1")
      startrow : upper left cell row to dump data frame.
                 Per default (startrow=None) calculate the last row
                 in the existing DF and write to the next row...
      truncate_sheet : truncate (remove and recreate) [sheet_name]
                       before writing DataFrame to Excel file
      to_excel_kwargs : arguments which will be passed to `DataFrame.to_excel()`
                        [can be dictionary]

    Returns: None
    """
    # ignore [engine] parameter if it was passed
    if "engine" in to_excel_kwargs:
        to_excel_kwargs.pop("engine")

    writer = pd.ExcelWriter(filename, engine="openpyxl")

    # Python 2.x: define [FileNotFoundError] exception if it doesn"t exist
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = IOError

    if "index" not in to_excel_kwargs:
        to_excel_kwargs["index"] = False

    try:
        # try to open an existing workbook
        if "header" not in to_excel_kwargs:
            to_excel_kwargs["header"] = True
        writer.book = load_workbook(filename)

        # get the last row in the existing Excel sheet
        # if it was not specified explicitly
        if startrow is None and sheet_name in writer.book.sheetnames:
            startrow = writer.book[sheet_name].max_row
            to_excel_kwargs["header"] = False

        # truncate sheet
        if truncate_sheet and sheet_name in writer.book.sheetnames:
            # index of [sheet_name] sheet
            idx = writer.book.sheetnames.index(sheet_name)
            # remove [sheet_name]
            writer.book.remove(writer.book.worksheets[idx])
            # create an empty sheet [sheet_name] using old index
            writer.book.create_sheet(sheet_name, idx)

        # copy existing sheets
        writer.sheets = {ws.title: ws for ws in writer.book.worksheets}
    except FileNotFoundError:
        # file does not exist yet, we will create it
        to_excel_kwargs["header"] = True

    if startrow is None:
        startrow = 0

    # write out the new sheet
    df.to_excel(writer, sheet_name, startrow=startrow, **to_excel_kwargs)

    # save the workbook
    writer.save()


def is_db_validate():
    global today
    try:
        sql = f"SELECT * FROM foreign_ins_purchases.`{today}`"
        cur.execute(sql)
    except Exception:
        today = (is_datetime_conversion(today) - timedelta(days=1)).strftime("%Y%m%d")
        is_db_validate()
    finally:
        result_set = cur.fetchall()
        return result_set


def start_price_constrast_fluc_calculator(standard_price, check_prcie):
    result = round(((check_prcie - standard_price) / standard_price) * 100, 2,)
    return result


def time_minus(first, second):
    first = is_datetime_conversion(first)
    second = is_datetime_conversion(second)
    result = first - second
    print("---------------time minus-------------------")
    print(result, type(result))
    print("---------------time minus-------------------")
    return result


def is_fluctuation_validate(rate_3fluctuation=None):
    if rate_3fluctuation:
        if (
            fluctuation >= 3
            and rate_3fluctuation <= 3
            and int(data_today) >= int(next_day)
            or second_fluctuation >= 3
            and rate_3fluctuation <= 3
            and int(data_today) >= int(next_day)
        ):
            return True
    else:
        if (
            fluctuation >= 9
            and int(data_today) >= int(next_day)
            or second_fluctuation >= 9
            and int(data_today) >= int(next_day)
        ):
            return True
    return False


def get_rate_fluctuation(rate_fluctuation):
    if fluctuation >= rate_fluctuation:
        return fluctuation
    else:
        return second_fluctuation


def get_rate_fluctuation_day(rate_fluctuation):
    if fluctuation >= rate_fluctuation:
        return data_today
    else:
        data_nextday


def get_rate_fluctuation_price(rate_fluctuation):
    if fluctuation >= rate_fluctuation:
        return data_today_high_price
    else:
        return data_nextday_high_price


if __name__ == "__main__":
    while int(today) >= 20190328:

        today = (is_datetime_conversion(today) - timedelta(days=1)).strftime("%Y%m%d")
        result_set = is_db_validate()
        sub_day = (is_datetime_conversion(today) + timedelta(days=1)).strftime("%Y%m%d")
        three_percent_day = ""
        nine_percent_day = ""
        three_percent_price = ""
        nine_percent_price = ""

        for row in result_set:
            name = row[2]
            print(name, today)
            code = row[1]
            next_day = row[15]
            next_day_start_price = row[19]
            next_day_end_price = row[16]
            rate_3fluctuation = row[17]
            rate_9fluctuation = 0
            if "KODEX" not in name and "TIGER 200" not in name:
                if isinstance(rate_3fluctuation, str):
                    rate_3fluctuation = 0
                if rate_3fluctuation >= 9:
                    rate_9fluctuation = rate_3fluctuation
                elif rate_3fluctuation < 3:
                    while (
                        rate_3fluctuation < 3
                        and rate_9fluctuation < 9
                        or int(datetime.today().strftime("%Y%m%d")) > int(sub_day)
                    ):
                        kiwoom.set_input_value("종목코드", code)
                        kiwoom.set_input_value("조회일자", sub_day)
                        kiwoom.set_input_value("표시구분", 1)
                        time.sleep(3.6)
                        kiwoom.comm_rq_data("opt10086_req", "opt10086", 0, "0101")
                        if (
                            is_datetime_conversion(sub_day) < datetime.today()
                            and next_day_start_price
                        ):
                            data = kiwoom.next_day_comparison
                            kiwoom.on_excel_sw = True
                            print(kiwoom.excel_assist_data)
                            data_today = data["당일"]
                            data_nextday = data["명일"] if data["명일"] else ""
                            data_today_high_price = data["당일고가"]
                            data_nextday_high_price = (
                                data["명일고가"] if data["명일고가"] else ""
                            )

                            # 등락률
                            fluctuation = start_price_constrast_fluc_calculator(
                                next_day_start_price, data_today_high_price
                            )

                            # 등락률
                            if data_nextday_high_price:
                                second_fluctuation = start_price_constrast_fluc_calculator(
                                    next_day_start_price, data_nextday_high_price
                                )
                                # 3% 확인
                            if is_fluctuation_validate(rate_3fluctuation):

                                rate_3fluctuation = get_rate_fluctuation(3)
                                three_percent_day = get_rate_fluctuation_day(3)
                                three_percent_price = get_rate_fluctuation_price(9)
                                print(
                                    "--------------------3percent check----------------"
                                )
                                print(
                                    f"data_today : {data_today} 고가 : {data_today_high_price} data_nextday : {data_nextday} 고가 : {data_nextday_high_price} name : {name}  rate_3fluctuation :{rate_3fluctuation} fluctuation : {fluctuation} second_fluctuation: {second_fluctuation}"
                                )
                                print(
                                    "--------------------3percent check----------------"
                                )
                            # 9% 확인
                            if is_fluctuation_validate():
                                rate_9fluctuation = get_rate_fluctuation(9)
                                nine_percent_day = get_rate_fluctuation_day(9)
                                nine_percent_price = get_rate_fluctuation_price(9)
                                print(
                                    "--------------------9percent check----------------"
                                )
                                print(
                                    f"rate_9fluctuation : {rate_9fluctuation} nine_percent_day:{nine_percent_day} nine_percent_price : {nine_percent_price}"
                                )
                                print(
                                    "--------------------9percent check----------------"
                                )
                            if rate_3fluctuation >= 3 and rate_9fluctuation >= 9:
                                print("-----------------break--------------")
                                print(
                                    f"name : {name} rate_3fluctuation : {rate_3fluctuation} rate_9fluctuation: {rate_9fluctuation}"
                                )
                                print("-----------------break--------------")
                                break  # 3% 등락률 9% 등락률을 다 충족했을 시 break
                        sub_day = (
                            is_datetime_conversion(sub_day) + timedelta(days=2)
                        ).strftime("%Y%m%d")

                        if int(sub_day) >= int(datetime.today().strftime("%Y%m%d")):
                            sub_day = (
                                is_datetime_conversion(today) + timedelta(days=1)
                            ).strftime("%Y%m%d")
                            break

                data_box = [
                    {
                        "날짜": today,
                        "종목": name,
                        "일일외인순매수": int(row[6]),
                        "일일기관순매수": int(row[7]),
                        "일일외인기관순매수": int(row[6]) + int(row[7]),
                        "당일시가": row[11],
                        "당일전일대비등락률": row[14],
                        "명일전일대비등락률": row[-1],
                        "명일고가등락률": row[17],
                        "명일": next_day,
                        "명일시가": next_day_start_price,
                        "up3%날짜": three_percent_day if three_percent_day else next_day,
                        "up3%걸린시간": time_minus(three_percent_day, next_day)
                        if three_percent_day
                        else 0
                        if rate_3fluctuation >= 3
                        else "",
                        "up3%perscent": rate_3fluctuation
                        if rate_3fluctuation >= 3
                        else "",
                        "up3%price": str(three_percent_price)
                        if three_percent_price
                        else str(next_day_end_price)
                        if rate_3fluctuation >= 3
                        else "",
                        "up9%날짜": str(nine_percent_day),
                        "up9%걸린시간": time_minus(nine_percent_day, next_day)
                        if nine_percent_day
                        else 0
                        if rate_3fluctuation >= 9
                        else "",
                        "up9%percent": rate_9fluctuation
                        if rate_9fluctuation
                        else rate_3fluctuation
                        if rate_3fluctuation >= 9
                        else "",
                        "up9%price": nine_percent_price if nine_percent_price else "",
                    }
                ]

                df = pd.DataFrame(
                    data_box,
                    columns=[
                        "날짜",
                        "종목",
                        "일일외인순매수",
                        "일일기관순매수",
                        "일일외인기관순매수",
                        "당일시가",
                        "당일전일대비등락률",
                        "명일전일대비등락률",
                        "명일고가등락률",
                        "명일",
                        "명일시가",
                        "up3%날짜",
                        "up3%걸린시간",
                        "up3%perscent",
                        "up3%price",
                        "up9%날짜",
                        "up9%걸린시간",
                        "up9%percent",
                        "up9%price",
                    ],
                )
                append_df_to_excel(
                    "./기록용/test.xlsx",
                    df,
                    "Sheet1",
                    startrow=excel_row,
                    truncate_sheet=False,
                    header=None,
                )
                print(excel_row)
                excel_row += 1

                three_percent_day = ""
                nine_percent_day = ""
                three_percent_price = ""
                nine_percent_price = ""

