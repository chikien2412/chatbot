from typing import Any, Text, Dict, List, Union, Optional
from dotenv import load_dotenv
from rasa_sdk.forms import FormValidationAction
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import json
import re
import sqlite3
import requests
import os

load_dotenv()

sqliteConnection = sqlite3.connect('pythonsqlite.db')
cursor = sqliteConnection.cursor()
print("Database created and Successfully Connected to SQLite")
        
def name_cap(text):
    tarr = text.split()
    for idx in range(len(tarr)):
        tarr[idx] = tarr[idx].capitalize()
    return ' '.join(tarr)


airtable_api_key=os.getenv("AIRTABLE_API_KEY")
base_id=os.getenv("BASE_ID")
table_name=os.getenv("TABLE_NAME")

def create_health_log(cauhoi, thongtin, ten):
    request_url=f"https://api.airtable.com/v0/app3f3oH1WCFaWxsm/CAUHOI_DHTL"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer keyez1auPKPuARPVi",
    }  
    data = {
        "fields": {
            "cauhoi": cauhoi,
            "thongtin": thongtin,
            "ten": ten,
        }
    }
    try:
        response = requests.post(
            request_url, headers=headers, data=json.dumps(data)
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
    return response
    print(response.status_code)


class ActionSubmitResults(Action):
    def name(self) -> Text:
        return "action_submit_results"
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        cauhoi = tracker.get_slot("cauhoi")
        thongtin = tracker.get_slot("thongtin")
        ten = tracker.get_slot("cust_name")

        response = create_health_log(
                cauhoi=cauhoi,
                thongtin=thongtin,
                ten=ten
            )

        dispatcher.utter_message("Thông tin của bạn đã được lưu!")
        return []


class ActionAskKnowledgeBaseDIEMCHUAN(Action):

    def name(self) -> Text:
        return "action_custom_diem_chuan"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        text_input = text.lower()
        print(text_input)
        name_cap(text_input)
        Diem = tracker.get_slot("diem")
        ten_nganh_sl = tracker.get_slot("nganh").lower()
        nam_sl = tracker.get_slot("nam")
        print(Diem)
        print(ten_nganh_sl)
        print(nam_sl)
        check = False
        if nam_sl == None: 
            check = True
            dispatcher.utter_message("Bạn cần nhập đầy đủ tên ngành và năm ạ")
        elif nam_sl not in ['2020','2021']:
            dispatcher.utter_message("Xin lỗi bạn! Tôi mới cập nhật dữ liệu cho hai năm gần đây nhất.")
        else:
            sqlite_select_query = "SELECT * from TUYENSINH where nam="+ nam_sl
            cursor.execute(sqlite_select_query)
            record = cursor.fetchall()
            #print(record)
            for index in record:
                ma_nganh = index[1]
                ten_nganh = index[2]
                diem_chuan = index[3]
                chi_tieu = index[4]
                nam = index[5]
                to_hop_mon = index[6]
                if ten_nganh_sl in ten_nganh :
                    check = True
                    dispatcher.utter_message("Ngành "+ str(ten_nganh) + " năm " + str(nam) + " có điểm chuẩn là: " + str(diem_chuan))
            if not check:
                dispatcher.utter_message("Trường Đại học Thủy Lợi không đào tạo ngành "+str(ten_nganh_sl)+ " này năm 2020. Mời bạn nhập lại tên ngành")
                
class ActionAskKnowledgeBaseCHITIEU(Action):

    def name(self) -> Text:
        return "action_custom_chi_tieu"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        text_input = text.lower()
        name_cap(text_input)
        CT = tracker.get_slot("so_luong")
        ten_nganh_slot = tracker.get_slot("nganh").lower()
        nam_slot = tracker.get_slot("nam")
        print(CT)
        print(ten_nganh_slot)
        print(nam_slot)
        check = False
        if nam_slot == None:
            check = True
            dispatcher.utter_message("Bạn cần nhập đầy đủ chỉ tiêu tên ngành và năm ạ")
        elif nam_slot not in ['2020','2021']:
            dispatcher.utter_message("Xin lỗi bạn! Tôi mới cập nhật dữ liệu cho hai năm gần đây nhất.")
        else:
            sqlite_select_Query = "SELECT * from TUYENSINH where nam="+nam_slot
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            #print(record)
            for index in record:
                ma_nganh = index[1]
                ten_nganh = index[2]
                diem_chuan = index[3]
                chi_tieu = index[4]
                nam = index[5]
                to_hop_mon = index[6]
                if ten_nganh_slot in ten_nganh:
                    check = True
                    dispatcher.utter_message( "Ngành " + str(ten_nganh) + " năm " + str(nam) +  " có chỉ tiêu là: " + str(chi_tieu))   
            if not check:
                dispatcher.utter_message("Trường Đại học Thủy Lợi không đào tạo Ngành : " + str(ten_nganh_slot) + " này năm 2020. Mời bạn nhập năm 2021.")
            
class ActionAskKnowledgeBaseMANGANH(Action):

    def name(self) -> Text:
        return "action_custom_ma_nganh"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        text_input = text.lower()
        name_cap(text_input)
        ma_nganh_hm = tracker.get_slot("ma")
        ten_nganh_hm = tracker.get_slot("nganh").lower()
        print(ma_nganh_hm)
        print(ten_nganh_hm)
        sqlite_select_Query = "SELECT * from TUYENSINH where nam=2021"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        #print(record)
        check = False
        for index in record:
            ma_nganh = index[1]
            ten_nganh = index[2]
            diem_chuan = index[3]
            chi_tieu = index[4]
            nam = index[5]
            to_hop_mon = index[6]
            if ten_nganh_hm in ten_nganh:
                check = True
                dispatcher.utter_message("Mã ngành "+ str(ten_nganh)+" là: " + str(ma_nganh))   
        if not check:
            dispatcher.utter_message("Tên ngành ["+str(ten_nganh_hm)+ " ] không hợp lệ. Mời bạn nhập lại tên ngành ạ")

class ActionAskKnowledgeBaseTOHOPMON(Action):

    def name(self) -> Text:
        return "action_custom_to_hop_mon"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        text_input = text.lower()
        name_cap(text_input)
        to_hop_mon_thm = tracker.get_slot("tohopmon")
        ten_nganh_thm = tracker.get_slot("nganh").lower()
        print(to_hop_mon_thm)
        print(ten_nganh_thm)
        sqlite_select_Query = "SELECT * from TUYENSINH where nam=2021"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        #print(record)
        check = False
        for index in record:
            ma_nganh = index[1]
            ten_nganh = index[2]
            diem_chuan = index[3]
            chi_tieu = index[4]
            nam = index[5]
            to_hop_mon = index[6]
            if ten_nganh_thm in ten_nganh:
                check = True
                dispatcher.utter_message("Tổ hợp môn của ngành "+ str(ten_nganh)+" là: " + str(to_hop_mon))   
        if not check:
            dispatcher.utter_message("Tên ngành [ "+str(ten_nganh_thm)+ " ] này không hợp lệ. Mời bạn nhập lại chính xác thông tin tên ngành")

class ActionAskKnowledgeBaseNGANHHOC(Action):

    def name(self) -> Text:
        return "action_custom_nganh_hoc"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        text_input = text.lower()
        name_cap(text_input)
        ten_nganh_hoc = tracker.get_slot("nganh").lower()
        print(ten_nganh_hoc)
        sqlite_select_Query = "SELECT * from TUYENSINH where nam=2021"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        #print(record)
        check = False
        for index in record:
            ma_nganh = index[1]
            ten_nganh = index[2]
            diem_chuan = index[3]
            chi_tieu = index[4]
            nam = index[5]
            to_hop_mon = index[6]
            if ten_nganh_hoc in ten_nganh:
                check = True
                dispatcher.utter_message("Trường Đại học Thủy Lợi có đào tạo ngành "+ str(ten_nganh_hoc)+" bạn nhé ") 
                break  
        if not check:
            dispatcher.utter_message("Trường Đại học Thủy Lợi không đào tạo ngành "+str(ten_nganh_hoc)+ " này ạ. Mời bạn nhập lại chính xác thông tin tên ngành")

class ActionAskKnowledgeBaseMOTANGANH(Action):

    def name(self) -> Text:
        return "action_custom_mo_ta_nganh"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        text_input = text.lower()
        name_cap(text_input)
        mo_ta_nganh_mt = tracker.get_slot("mota")
        print(mo_ta_nganh_mt)
        ten_nganh_mt = tracker.get_slot("nganh").lower()
        print(ten_nganh_mt)
        sqlite_select_Query = "SELECT * from MOTA"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        #print(record)
        check = False
        for index in record:
            ten_nganh = index[1]
            mo_ta_nganh = index[2]
            if ten_nganh_mt in ten_nganh:
                check = True
                dispatcher.utter_message("Thông tin về ngành "+ str(ten_nganh)+" là: " + str(mo_ta_nganh))   
        if not check:
            dispatcher.utter_message("Tên ngành [ "+str(ten_nganh_mt)+ " ] này không hợp lệ. Mời bạn nhập lại chính xác thông tin tên ngành")



