class TrainData():
    def __init__(self, line, train_id, first_station, last_station, planned_departure, current_departure, track, message, train_station):
        self.line = line
        self.train_id = train_id
        self.first_station = first_station
        self.last_station = last_station
        self.planned_departure = planned_departure
        self.current_departure = current_departure
        self.track = track
        self.message = message
        self.train_station = train_station