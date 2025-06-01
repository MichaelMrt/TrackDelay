from train_delay_tracker import TrainDelayTracker, AuthData, DatabaseConfig
import config


auth_data = AuthData(config.CLIENT_ID, config.CLIENT_SECRET)
database_config = DatabaseConfig(config.DB_HOSTNAME, config.DB_USER, config.DB_PASSWORD, config.DATABASE)
train_delay_tracker = TrainDelayTracker(auth_data, database_config)

train_delay_tracker.track_station("Bonn")
train_delay_tracker.track_station("Köln")
train_delay_tracker.track_station("Münster")
train_delay_tracker.track_station("Düsseldorf Hbf")
train_delay_tracker.track_station("Duisburg")
train_delay_tracker.track_station("Essen")
train_delay_tracker.track_station("Wuppertal")
train_delay_tracker.track_station("Bochum")
train_delay_tracker.track_station("Berlin Hbf")
train_delay_tracker.track_station("Lünen")
train_delay_tracker.track_station("Ennepetal") 
