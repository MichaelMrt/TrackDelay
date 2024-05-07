import deutsche_bahn_api.api_authentication as dba
import deutsche_bahn_api.station_helper
import deutsche_bahn_api.timetable_helper
import config
import mysql.connector
import datetime
import os

class Api_wrapper:
    
    def _dataset_is_new(self,mycursor, planned_departure, current_departure, train_id):
        mycursor.execute("SELECT * FROM test")
        results = mycursor.fetchall()

        for result in results:
            if (result[2] == train_id or result[5] == planned_departure or result[6] == current_departure):
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
        print(found_stations_by_name[0][3]) # Output station
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
            

            track = train.platform
            messages = train.train_changes.messages


            string_message = ""

            for message_object in messages:
                string_message += str(message_object.message) + " | "

           # self._debug_output(line,train_id,first_station,last_station,planned_departure,current_departure,track,string_message,train_station_name)
            
            if self._dataset_is_new(mycursor, planned_departure, current_departure, train_id):
                query = "INSERT INTO trains VALUES (DEFAULT,'" + line + "','" + train_id + "','" + first_station + "','" + last_station + "','" + planned_departure + "','" + current_departure + "','" + track + "','" + string_message +"','"+train_station_name+"')"
                print("Dataset inserted: "+line+" "+train_id)
                mycursor.execute(query)
                mydb.commit()

        mydb.close()
        
        print("End of script "+str(datetime.datetime.now()))

        log_path = os.path.join('logs', 'logs.log')
        with open(log_path,'w') as log_file:
            log_file.write("End of script "+str(datetime.datetime.now())+"\n")
        log_file.close()

