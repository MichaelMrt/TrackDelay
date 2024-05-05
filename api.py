import deutsche_bahn_api.api_authentication as dba
import deutsche_bahn_api.station_helper
import deutsche_bahn_api.timetable_helper
import config
import mysql.connector

# Connect to Database
mydb = mysql.connector.connect(
  host=config.DB_HOSTNAME,
  user=config.DB_USER,
  password=config.DB_PASSWORD,
  database=config.DATABASE
)

mycursor = mydb.cursor()
mycursor.execute("SELECT count(*) FROM main")
#results = mycursor.fetchall()

api = dba.ApiAuthentication(config.CLIENT_ID, config.CLIENT_SECRET)
success: bool = api.test_credentials()

station_helper = deutsche_bahn_api.station_helper.StationHelper()
found_stations_by_name = station_helper.find_stations_by_name("Lünen")

timetable_helper = deutsche_bahn_api.timetable_helper.TimetableHelper(found_stations_by_name[0], api)
trains_in_this_hour = timetable_helper.get_timetable()
trains_with_changes = timetable_helper.get_timetable_changes(trains_in_this_hour)

for train in trains_with_changes:
    line = str(train.train_type) + str(train.train_line)
    id = str(train.train_number)
    first_station = train.passed_stations.split("|")[0]
    last_station = train.stations.split("|")[-1]
    planned_departure = train.departure
    current_departure = train.train_changes.departure
    track = train.platform
    messages = train.train_changes.messages
    station = "Lünen"
    
    string_message =""
    for message_object in messages:
        string_message += str(message_object.message)+" | "

 #ToDo Add SQL Insert

mydb.close()