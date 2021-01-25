import sys
import pandas as pd
import time
import sqlite3
import threading
from datetime import datetime, timedelta
from collections import Counter
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from holiday_calculator import (
    count_holiday,
    stock_today,
    holiday_is_valid,
    next_day,
    is_datetime_conversion,
)

TR_REQ_TIME_INTERVAL = 1.7
SQLITE = sqlite3.connect("c:/1.python_project/stock_alarm_telegram_bot/sqlite3.db")


def DAY(i=0):
    return datetime.today() - timedelta(days=i)


def TODAY(i=0):
    return DAY(i).strftime("%Y%m%d")


def NEXT_DAY(i=0):
    day = DAY(i) + timedelta(days=1)
    return day.strftime("%Y%m%d")


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()
        self.purchases_foreign_institution_box = []
        self.comprehensive_data = []

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(";")
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall(
            "CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no
        )
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall(
            "CommGetData(QString, QString, QString, int, QString",
            code,
            real_type,
            field_name,
            index,
            item_name,
        )
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(
        self,
        screen_no,
        rqname,
        trcode,
        record_name,
        next,
        unused1,
        unused2,
        unused3,
        unused4,
    ):
        # OnReceiveTrData 이벤트가 발생할 때 PrevNext 라는 인자 값을 통해
        # 연속조회가 필요 한 경우 값을 2로 리턴함 더 받아오기 위해 스위치설정
        if next == "2":
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt90009_req":
            self._opt90009(rqname, trcode)

        if rqname == "opt10061_req":
            self._opt10061(rqname, trcode)

        if rqname == "opt10086_req":
            self._opt10086(rqname, trcode)
        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt90009(self, rqname, trcode):  # 외인, 기관 매수종목
        data_cnt = self._get_repeat_cnt(trcode, rqname)
        foreign_data_list = []
        institution_data_list = []

        for i in range(data_cnt):
            foreign_purchase_code = self._comm_get_data(
                trcode, "", rqname, i, "외인순매수종목코드"
            )
            foreign_purchase_stock = self._comm_get_data(
                trcode, "", rqname, i, "외인순매수종목명"
            )
            foreign_purchase_amount = self._comm_get_data(
                trcode, "", rqname, i, "외인순매수금액"
            )
            foreign_purchase_volume = self._comm_get_data(
                trcode, "", rqname, i, "외인순매수수량"
            )
            institution_purchase_code = self._comm_get_data(
                trcode, "", rqname, i, "기관순매수종목코드"
            )
            institution_purchase_stock = self._comm_get_data(
                trcode, "", rqname, i, "기관순매수종목명"
            )
            institution_purchase_amount = self._comm_get_data(
                trcode, "", rqname, i, "기관순매수금액"
            )
            institution_purchase_volume = self._comm_get_data(
                trcode, "", rqname, i, "기관순매수수량"
            )

            foreign_data_list.append(
                {
                    "종목코드": foreign_purchase_code,
                    "종목명": foreign_purchase_stock,
                    "외인순매수금액": foreign_purchase_amount,
                    "외인순매수수량": foreign_purchase_volume,
                }
            )

            institution_data_list.append(
                {
                    "종목코드": institution_purchase_code,
                    "종목명": institution_purchase_stock,
                    "기관순매수금액": institution_purchase_amount,
                    "기관순매수수량": institution_purchase_volume,
                }
            )
        # 기관 , 외인 둘 다 매수한 종목
        for foreign_data in foreign_data_list:
            for institution_data in institution_data_list:
                if foreign_data["종목명"] == institution_data["종목명"]:
                    self.purchases_foreign_institution_box.append(
                        {
                            **foreign_data,
                            "기관순매수금액": institution_data["기관순매수금액"],
                            "기관순매수수량": institution_data["기관순매수수량"],
                        }
                    )

    def _opt10061(self, rqname, trcode):  # 지정일자 개인, 외인 , 기관 매수액
        individual_purchase = self._comm_get_data(trcode, "", rqname, 0, "개인투자자")
        foreign_purchase = self._comm_get_data(trcode, "", rqname, 0, "외국인투자자")
        institution_purchase = self._comm_get_data(trcode, "", rqname, 0, "기관계")
        self.comprehensive_data.append(
            {
                "종목코드": "",
                "종목명": "",
                "개인": individual_purchase,
                "외국인": foreign_purchase,
                "기관": institution_purchase,
            }
        )

    def _opt10086(self, rqname, trcode):
        self.next_day_comparison = {}
        for i in range(2):  # 당일과 명일 데이터만 받아옴
            date = self._comm_get_data(trcode, "", rqname, i, "날짜")
            high_price = int(
                self._comm_get_data(trcode, "", rqname, i, "고가")
                .replace("+", "")
                .replace("-", "")
            )
            start_price = int(
                self._comm_get_data(trcode, "", rqname, i, "시가")
                .replace("+", "")
                .replace("-", "")
            )
            low_price = int(
                self._comm_get_data(trcode, "", rqname, i, "저가")
                .replace("+", "")
                .replace("-", "")
            )
            end_price = int(
                self._comm_get_data(trcode, "", rqname, i, "종가")
                .replace("+", "")
                .replace("-", "")
            )
            percent = self._comm_get_data(trcode, "", rqname, i, "등락률")
            if i == 0 and date == TODAY:
                self.next_day_comparison = {
                    "명일": NEXT_DAY,
                    "명일고가": "",
                    "명일고가등락률": "",
                    "전일종가대비명일고가등락률": "",
                    "명일저가": "",
                    "명일시가": "",
                    "명일종가": "",
                    "명일전일대비등락률": "",
                    "당일": date,
                    "당일고가": high_price,
                    "당일고가등락률": round(
                        ((high_price - start_price) / start_price) * 100, 2
                    ),
                    "당일저가": low_price,
                    "당일시가": start_price,
                    "당일종가": end_price,
                    "당일전일대비등락률": percent,
                }
                break
            elif i == 0:
                self.next_day_comparison = {
                    "명일": date,
                    "명일고가": high_price,
                    "명일고가등락률": round(
                        ((high_price - start_price) / start_price) * 100, 2
                    ),
                    "전일종가대비명일고가등락률": "",
                    "명일저가": low_price,
                    "명일시가": start_price,
                    "명일종가": end_price,
                    "명일전일대비등락률": percent,
                }
            else:
                if self.next_day_comparison["명일고가"]:
                    self.next_day_comparison["전일종가대비명일고가등락률"] = round(
                        ((self.next_day_comparison["명일고가"] - end_price) / end_price)
                        * 100,
                        2,
                    )
                self.next_day_comparison["당일"] = date
                self.next_day_comparison["당일고가"] = high_price
                self.next_day_comparison["당일고가등락률"] = round(
                    ((high_price - start_price) / start_price) * 100, 2
                )
                self.next_day_comparison["당일저가"] = low_price
                self.next_day_comparison["당일시가"] = start_price
                self.next_day_comparison["당일종가"] = end_price
                self.next_day_comparison["당일전일대비등락률"] = percent


def request_opt90009(next):  # 외인, 기관 매수종목

    kiwoom.set_input_value("시장구분", "000")
    kiwoom.set_input_value("금액수량구분", "1")
    kiwoom.set_input_value("조회일자구분", "1")
    kiwoom.set_input_value("날짜", TODAY)
    kiwoom.comm_rq_data("opt90009_req", "opt90009", next, "0101")


# 해당일자부터 5일전까지 외인 , 기관 매수액
def request_opt10061(kiwoom, data, index):
    kiwoom.set_input_value("종목코드", data["종목코드"])
    kiwoom.set_input_value(
        "시작일자",
        (
            is_datetime_conversion(TODAY)
            - timedelta(days=5)
            - timedelta(days=count_holiday())
        ).strftime("%Y%m%d"),
    )
    kiwoom.set_input_value("종료일자", TODAY)
    kiwoom.set_input_value("금액수량구분", "1")
    kiwoom.set_input_value("매매구분", "0")
    kiwoom.set_input_value("단위구분", "1000")
    time.sleep(TR_REQ_TIME_INTERVAL)
    kiwoom.comm_rq_data("opt10061_req", "opt10061", 0, "0101")
    comprehensive_data = kiwoom.comprehensive_data[index]
    comprehensive_data["종목코드"] = data["종목코드"]
    comprehensive_data["종목명"] = data["종목명"]
    comprehensive_data["일일외인순매수"] = data["외인순매수금액"]
    comprehensive_data["일일기관순매수"] = data["기관순매수금액"]


def request_opt10086(kiwoom, data, index):
    kiwoom.set_input_value("종목코드", data["종목코드"])
    kiwoom.set_input_value("조회일자", NEXT_DAY)
    kiwoom.set_input_value("표시구분", 1)
    kiwoom.comm_rq_data("opt10086_req", "opt10086", 0, "0101")
    comprehensive_data = kiwoom.comprehensive_data[index]
    next_day_comparison = kiwoom.next_day_comparison
    comprehensive_data.update(next_day_comparison)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    for i in range(4):
        TODAY = (stock_today(datetime.today()) - timedelta(days=i)).strftime("%Y%m%d")
        print(TODAY)
        NEXT_DAY = next_day(TODAY).strftime("%Y%m%d")
        request_opt90009(0)  # 외인, 기관 매수종목
        if kiwoom.purchases_foreign_institution_box:
            for index, data in enumerate(kiwoom.purchases_foreign_institution_box):
                print(
                    f"Loading {index+1} ... {len(kiwoom.purchases_foreign_institution_box)}"
                )
                request_opt10061(kiwoom, data, index)  # 해당일자부터 5일전까지 외인 , 기관 매수액
                request_opt10086(kiwoom, data, index)
                """while kiwoom.remained_data == True:  # 연속조회가 필요한 경우
                    print("연속 조회 중...")
                    time.sleep(TR_REQ_TIME_INTERVAL)
                    request_opt90009(2)  # 외인, 기관 매수종목"""

            foreign_institution_dataframe = pd.DataFrame(
                kiwoom.purchases_foreign_institution_box,
                columns=["종목코드", "종목명", "외인순매수금액", "외인순매수수량", "기관순매수금액", "기관순매수수량"],
            )
            comprehensive_dataframe = pd.DataFrame(
                kiwoom.comprehensive_data,
                columns=[
                    "종목코드",
                    "종목명",
                    "개인",
                    "외국인",
                    "기관",
                    "일일외인순매수",
                    "일일기관순매수",
                    "당일",
                    "당일고가",
                    "당일고가등락률",
                    "당일시가",
                    "당일저가",
                    "당일종가",
                    "당일전일대비등락률",
                    "명일",
                    "명일고가",
                    "명일고가등락률",
                    "명일저가",
                    "명일시가",
                    "명일종가",
                    "명일전일대비등락률",
                ],
            )

            foreign_institution_dataframe.to_sql(TODAY, SQLITE, if_exists="replace")
            comprehensive_dataframe.to_sql(
                f"total_{TODAY}", SQLITE, if_exists="replace"
            )

            kiwoom.comprehensive_data = []
            kiwoom.purchases_foreign_institution_box = []
            kiwoom.next_day_comparison = []