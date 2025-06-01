from deutsche_bahn_api import *
import config
import train_data
import mysql.connector
import datetime 
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(SCRIPT_DIR, "..", "logs","logs.log")

class TrainDelayTracker:

    def track_train_station(self, train_station_name_userinput):
        train_station_data = self.get_station_data(train_station_name_userinput) 
        self.train_station_name = train_station_data[3]
        trains_in_this_hour = self.get_trains_in_this_hour(train_station_data)
        self.to_database(trains_in_this_hour)


    def get_station_data(self, train_station_name):
        station_helper = StationHelper()
        found_stations_by_name = station_helper.find_stations_by_name(train_station_name)
        station_data = found_stations_by_name[0]
        return station_data
    
    def get_trains_in_this_hour(self, train_station_data):
        api_auth = ApiAuthentication(config.CLIENT_ID, config.CLIENT_SECRET)
        timetable_helper = TimetableHelper(train_station_data, api_auth)
        timetable = timetable_helper.get_timetable()
        trains_in_this_hour = timetable_helper.get_timetable_changes(timetable)
        return trains_in_this_hour
    
    def prepare_trains_data(self, trains_list):
        trains_list_prepared = []
        for train in trains_list:
            line = self.get_trainline(train)
            train_id = train.train_number
            first_station = self.get_first_station(train)
            last_station = train.stations.split("|")[-1]
            planned_departure = train.departure
            current_departure = self.get_current_departure(train)
            track = train.platform
            messages = self.get_train_message(train.train_changes.messages)
            train_station = self.train_station_name

            trainData = train_data.TrainData(line, train_id, first_station, last_station, planned_departure, current_departure, track, messages, train_station)
            trains_list_prepared.append(trainData)
        return trains_list_prepared

    def get_trainline(self, train):
            if hasattr(train,'train_line'):
                line = str(train.train_type) + str(train.train_line)
            else: line = str(train.train_type)
            return line
    
    def get_first_station(self, train):
            if hasattr(train, 'passed_stations'):
                first_station = train.passed_stations.split("|")[0]
            else:
                 first_station = train.stations.split("|")[0]
            return first_station
                 
    def get_current_departure(self, train):
                if hasattr(train.train_changes, 'departure'):
                    current_departure = train.train_changes.departure
                else:
                    current_departure = None
                return current_departure
    
    def get_train_message(self, message_object_list):
         message_string = ""
         for message_object in message_object_list:
              message_string += str(message_object.message)
         return message_string
         
    def to_database(self, trains_list):
         trains_data_prepared = self.prepare_trains_data(trains_list)
         database_connection = mysql.connector.connect(host=config.DB_HOSTNAME, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DATABASE)
         database_cursor = database_connection.cursor()

         for trainData in trains_data_prepared:
            if self.dataset_is_new(database_cursor, trainData.planned_departure, trainData.current_departure, trainData.train_id):    
                self.add_to_database(database_cursor, trainData)
                database_connection.commit()
         database_connection.close()
         self.log(trainData.train_station)
         
    def dataset_is_new(self, mycursor, planned_departure, current_departure, train_id):
        mycursor.execute("SELECT * FROM trains ORDER by planned_departure DESC LIMIT 10000")
        results = mycursor.fetchall()
        for result in results:
            # Format the String date to a datetime object to compare with database results
            # Incoming String: 2405162133 -> 16th May 2024 21:33
            if isinstance(planned_departure, str): # api delivers string or date for some reason
             planned_departure = datetime.datetime.strptime(planned_departure, '%y%m%d%H%M') 
            if isinstance(current_departure, str):
             current_departure = datetime.datetime.strptime(current_departure, '%y%m%d%H%M')        

            if ((str(result[2]) == str(train_id) and str(result[5]) == str(planned_departure) and str(result[6]) == str(current_departure))):
                return False
        return True    
    
    def add_to_database(self, database_cursor, trainData):
        sql = "INSERT INTO trains VALUES (DEFAULT,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        parameters = (trainData.line, trainData.train_id, trainData.first_station, trainData.last_station, 
                      trainData.planned_departure,trainData.current_departure, trainData.track, 
                      trainData.message, trainData.train_station)
        print("Dataset inserted: "+trainData.line+" "+trainData.train_id)
        database_cursor.execute(sql, parameters)
        
    def log(self, train_station):
        print("End of script "+str(datetime.datetime.now())+" "+train_station)
        with open(LOG_PATH,'w') as log_file:
            log_file.write("End of script "+str(datetime.datetime.now())+" "+train_station+"\n") 
        log_file.close()