from deutsche_bahn_api.train import Train
from deutsche_bahn_api.train_changes import TrainChanges
from deutsche_bahn_api.message import Message
from deutsche_bahn_api import message as message
import deutsche_bahn_api.message as dbm
from deutsche_bahn_api.station_helper import StationHelper as StationHelper
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as elementTree
from sqlalchemy import create_engine
import pandas as pd
import time
import logging

class ApiAuthentication:
    def __init__(self, client_id, client_secret) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.stationEVA = 8000085

    def test_credentials(self) -> bool:
        response = requests.get(
            "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/station/BLS",
            headers={
                "DB-Api-Key": self.client_secret,
                "DB-Client-Id": self.client_id,
            }
        )
        return response.status_code == 200

    def get_headers(self) -> dict[str, str]:
        return {
                "DB-Api-Key": self.client_secret,
                "DB-Client-Id": self.client_id,
            }
    
    def get_timetable_xml(self, hour: [int] = None, date: [datetime] = None) -> str:
        hour_date: datetime = datetime.now()
        if hour:
            hour_date = datetime.strptime(str(hour), "%H")
        date_string: str = datetime.now().strftime("%y%m%d")
        if date is not None:
            date_string = date.strftime("%y%m%d")
        hour: str = hour_date.strftime("%H")
        response = requests.get(
            f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"
            f"/plan/{self.stationEVA}/{date_string}/{hour}",
            headers=self.get_headers()
        )
        if response.status_code == 410:
            return self.get_timetable_xml(int(hour), datetime.now() + timedelta(days=1))
        elif response.status_code == 401:
            raise Exception("Can't request timetable because the credentials are not correct. Please make sure that "
                            "you providing the correct credentials.")
        elif response.status_code != 200:
            raise Exception("Can't request timetable! The request failed with the HTTP status code {}: {}"
                            .format(response.status_code, response.text))
        return response.text
    
    def get_timetable_xml_hour_before(self, hour: [int] = None, date: [datetime] = None) -> str:
        hour_date: datetime = datetime.now()
        hour_date = hour_date - timedelta(hours=1)
        if hour:
            hour_date = datetime.strptime(str(hour), "%H")
        date_string: str = datetime.now().strftime("%y%m%d")
        if date is not None:
            date_string = date.strftime("%y%m%d")
        hour: str = hour_date.strftime("%H")
        response = requests.get(
            f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"
            f"/plan/{self.stationEVA}/{date_string}/{hour}",
            headers=self.get_headers()
        )
        if response.status_code == 410:
            return self.get_timetable_xml(int(hour), datetime.now() + timedelta(days=1))
        elif response.status_code == 401:
            raise Exception("Can't request timetable because the credentials are not correct. Please make sure that "
                            "you providing the correct credentials.")
        elif response.status_code != 200:
            raise Exception("Can't request timetable! The request failed with the HTTP status code {}: {}"
                            .format(response.status_code, response.text))
        return response.text
    
    def get_timetable(self, hour: [int] = None) -> list[Train]:
        train_list: list[Train] = []
        trains = elementTree.fromstringlist(self.get_timetable_xml(hour))
        for train in trains:
            trip_label_object: dict[str, str] | None = None
            arrival_object: dict[str, str] | None = None
            departure_object: dict[str, str] | None = None
            for train_details in train:
                if train_details.tag == "tl":
                    trip_label_object = train_details.attrib
                if train_details.tag == "dp":
                    departure_object = train_details.attrib
                if train_details.tag == "ar":
                    arrival_object = train_details.attrib

            if not departure_object:
                """ Arrival without department """
                continue

            train_object: Train = Train()
            train_object.stop_id = train.attrib["id"]
            train_object.train_type = trip_label_object["c"]
            train_object.train_number = trip_label_object["n"]
            train_object.platform = departure_object['pp']
            train_object.stations = departure_object['ppth']
            train_object.departure = departure_object['pt']

            if "f" in trip_label_object:
                train_object.trip_type = trip_label_object["f"]

            if "l" in departure_object:
                train_object.train_line = departure_object['l']

            if arrival_object:
                train_object.passed_stations = arrival_object['ppth']
                train_object.arrival = arrival_object['pt']

            train_list.append(train_object)

        return train_list

    def get_timetable_changes(self, trains: list) -> list[Train]:
        response = requests.get(
            f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/fchg/{self.stationEVA}",
            headers=self.get_headers()
        )
        changed_trains = elementTree.fromstringlist(response.text)

        train_list: list[Train] = []

        for changed_train in changed_trains:
            found_train: Train | None = None
            train_changes: TrainChanges = TrainChanges()
            train_changes.messages = []

            for train in trains:
                if train.stop_id == changed_train.attrib["id"]:
                    found_train = train

            if not found_train:
                continue

            for changes in changed_train:
                if changes.tag == "dp":
                    if "ct" in changes.attrib:
                        train_changes.departure = changes.attrib["ct"]
                    if "cpth" in changes.attrib:
                        train_changes.stations = changes.attrib["cpth"]
                    if "cp" in changes.attrib:
                        train_changes.platform = changes.attrib["cp"]

                if changes.tag == "ar":
                    if "ct" in changes.attrib:
                        train_changes.arrival = changes.attrib["ct"]
                    if "cpth" in changes.attrib:
                        train_changes.passed_stations = changes.attrib["cpth"]

                for message in changes:
                    new_message = Message()
                    new_message.id = message.attrib["id"]
                    new_message.code = message.attrib["c"]
                    new_message.time = message.attrib["ts"]
                    new_message.message = dbm.resolve_message_by_code(int(message.attrib["c"]))
                    train_changes.messages.append(new_message)

            found_train.train_changes = train_changes
            train_list.append(found_train)

        return train_list


df = pd.DataFrame(columns=["Bahnhof", "Linie", "BahnID", "Von", "Nach", "plan_abfahrt", "akt_abfahrt", "Meldung", "Gleis"])
api = ApiAuthentication("8f67e74b49f0ba8660339bb4cd826e98", "51a8654bf38ac547db6f60360673818d")
train = api.get_timetable()
now_init = datetime.now()
current_time_init = now_init.strftime('%H')

def start(first:bool):
    active = True
    arr_meldung = []

    while active:
        try:
            global df
            global current_time_init
            global train

            now = datetime.now()
            current_time = now.strftime('%H:%M')
            current_hour = now.strftime('%H')
            current_date = now.strftime('%d_%m_%y')
            now_delta_one_day = now + timedelta(1)
            tomorrow = now_delta_one_day.strftime('%y%m%d')
    
            if current_hour != current_time_init:
            
                current_time_init = now.strftime('%H')
                new_train = api.get_timetable()
                for j in new_train:
                    train.append(j)
                print(train)
            changes = api.get_timetable_changes(train)

            if first:
                first = False
                with open(f"logs/{current_date}log.txt", "w") as init:
                    init.write("")
        
            if len(train) == 0:
                with open(f"logs/{current_date}log.txt", "a", encoding="UTF-8") as log:
                    logtime = now.strftime('%H:%M:%S')
                    log.write(str(logtime) + " keine Züge vorhanden!\n")
                    time.sleep(1800)
                start(False)
                
            for i in changes:
                try:
                    arr1 = i.passed_stations.split("|")
                    arr2 = i.stations.split("|")

                    linie = str(i.train_type) + str(i.train_line)
                    id = str(i.train_number)
                    von = arr1[0]
                    nach = arr2[-1]
                    planm_abfahrt = i.departure
                    akt_abfahrt = i.train_changes.departure
                    arr_meldung = i.train_changes.messages
                    gleis = i.platform
                    meldung = ""
                    meldung_check = []

                except AttributeError:
                    continue
                
                if len(arr_meldung) > 0:
                    for msg in arr_meldung:
                        if str(msg.message) not in meldung_check:
                            meldung_check.append(str(msg.message))
                            meldung += " " + str(msg.message) + ","
                    meldung = meldung[:-1]

                # Überprüfen, ob die Linie mit der planmäßigen Abfahrt bereits existiert
                match = df[(df['BahnID'] == id) & (df['plan_abfahrt'] == planm_abfahrt)]

                if match.empty and (akt_abfahrt[0:6] != tomorrow):
                    with open(f"logs/{current_date}log.txt", "a", encoding="UTF-8") as log:
                        logtime = now.strftime('%H:%M:%S')
                        log.write(str(logtime) + " Verbindung gefunden: " + str(linie) + " ID: " + id + " nach " + str(nach) + "; Planmaessig um: " + str(planm_abfahrt) + "; aktuell: " + str(akt_abfahrt) + "; Grund: " + str(meldung) + "\n")
                    df = df._append({"Bahnhof": "Duesseldorf", "Linie": linie, "BahnID": id, "Von": von, "Nach": nach, 
                                "plan_abfahrt": planm_abfahrt, "akt_abfahrt": akt_abfahrt,
                                "Meldung": meldung, "Gleis": gleis}, ignore_index=True)
                else:
                    # Aktualisieren der aktuellen Abfahrt, falls notwendig
                    if df.at[match.index[0], 'akt_abfahrt'] != akt_abfahrt and akt_abfahrt != None:
                        df.at[match.index[0], 'akt_abfahrt'] = akt_abfahrt
                        with open(f"logs/{current_date}log.txt", "a", encoding="UTF-8") as log:
                            logtime = now.strftime('%H:%M:%S')
                            log.write(str(logtime) + " Neue Abfahrtszeit fuer: " + str(linie) + " ID: " + id + " nach " + str(nach) + "; Planmaessig um: " + str(planm_abfahrt) + "; aktuell: " + str(akt_abfahrt) + "; Grund:" + str(meldung) + "\n")
    
            if current_time != "21:58":
                with open("status.txt", "w") as w:
                    logtime = now.strftime('%H:%M:%S')
                    w.write(f"{logtime} active")
                time.sleep(20)
            else:
                active = False

        except AttributeError as aEx:
            if current_time != "23:58":
                with open("status.txt", "w") as w:
                    logtime = now.strftime('%H:%M:%S')
                    w.write(f"{logtime} active")
                time.sleep(20)
            else:
                active = False

        except Exception as ex:
            with open("status.txt", "w") as w:
                w.write("PROBLEM\n" + str(logging.exception(str(ex))))

    engine = create_engine('mysql+mysqlconnector://marco:Auto49!@80.158.78.110:3306/track_delay')
    
    df.to_sql('main', con=engine, if_exists='append', index=False)
    print("*********DATABASE**********")
    
start(True)
