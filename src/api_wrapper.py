import deutsche_bahn_api.api_authentication as dba
import deutsche_bahn_api.station_helper
import deutsche_bahn_api.timetable_helper
import mysql.connector
import datetime
import os
import sys

# Paths to script
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, "..", "src", "main.py")
log_path = os.path.join(script_dir, "..", "logs","logs.log")


# jump up one folder to import the config file
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

class Api_wrapper:
    
    def _dataset_is_new(self,mycursor, planned_departure, current_departure, train_id):
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
    
    def _debug_output(self,line,train_id,first_station,last_station,planned_departure,current_departure,track,messages,train_station):
        print("trainid: "+train_id)
        print("line: "+line)
        print("first_station:" +first_station)
        print("last_station: "+last_station)
        print("planned_departure: "+planned_departure)
        print("current_departure: "+current_departure)
        print("track: "+track)
        print("messages: "+messages)
        print("train_station: "+train_station)
        

    def start(self, train_station_name):
        # Connect to Database
        mydb = mysql.connector.connect(
            host=config.DB_HOSTNAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DATABASE
        )

        mycursor = mydb.cursor()

        api = dba.ApiAuthentication(config.CLIENT_ID, config.CLIENT_SECRET)

        station_helper = deutsche_bahn_api.station_helper.StationHelper()
        found_stations_by_name = station_helper.find_stations_by_name(train_station_name)

        train_station_name = found_stations_by_name[0][3]

        timetable_helper = deutsche_bahn_api.timetable_helper.TimetableHelper(found_stations_by_name[0], api)
        trains_in_this_hour = timetable_helper.get_timetable()
        trains_with_changes = timetable_helper.get_timetable_changes(trains_in_this_hour)

        for train in trains_with_changes:
            if hasattr(train,'train_line'):
             line = str(train.train_type) + str(train.train_line)
            else: line = str(train.train_type)

            train_id = str(train.train_number)

            # check if train has already passed stations
            if hasattr(train, 'passed_stations'):
                first_station = train.passed_stations.split("|")[0]
            else:
                first_station = train.stations.split("|")[0]

            last_station = train.stations.split("|")[-1]
            planned_departure = train.departure

            
            if hasattr(train.train_changes, 'departure'):
                current_departure = train.train_changes.departure
            else:
                current_departure = None
            

            track = train.platform
            messages = train.train_changes.messages


            string_message = ""

            for message_object in messages:
                string_message += str(message_object.message) + " | "

           # self._debug_output(line,train_id,first_station,last_station,planned_departure,current_departure,track,string_message,train_station_name)
            
            if self._dataset_is_new(mycursor, planned_departure, current_departure, train_id):
                sql = "INSERT INTO trains VALUES (DEFAULT,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                parameters = (line, train_id, first_station, last_station, planned_departure,current_departure, track, string_message, train_station_name)
                print("Dataset inserted: "+line+" "+train_id)
                mycursor.execute(sql,parameters)
                mydb.commit()

        mydb.close()
        
        print("End of script "+str(datetime.datetime.now())+" "+train_station_name)


        with open(log_path,'w') as log_file:
            log_file.write("End of script "+str(datetime.datetime.now())+" "+train_station_name+"\n") 
        log_file.close()

