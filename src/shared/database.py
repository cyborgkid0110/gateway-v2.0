import sqlite3
import datetime
from lib.dao import SqliteDAO

location = "./data/data.db"
def createDatabase():
    db = SqliteDAO(location)
    db.createTable("RoomInfo", """  room_id INTEGER PRIMARY KEY""")

    db.createTable("Registration", """  node_id INTEGER PRIMARY KEY, 
                                        function TEXT(50),
                                        sync_state TEXT(50),
                                        protocol TEXT(10), 
                                        time INTEGER""")

    db.createTable("BTMeshNodes", """   id INTEGER PRIMARY KEY AUTOINCREMENT
                                        node_id INTEGER
                                        uuid TEXT(40)
                                        unicast INTEGER
                                        mac TEXT(20)
                                        FOREIGN KEY (node_id) REFERENCES Registration (node_id) ON DELETE CASCADE ON UPDATE CASCADE""")

    db.createTable("SensorMonitor", """ id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        node_id INTEGER,
                                        co2 INTEGER DEFAULT -1,
                                        temp REAL DEFAULT -1.0,
                                        hum REAL DEFAULT -1.0,
                                        light REAL DEFAULT -1.0,
                                        sound REAL DEFAULT -1.0,
                                        dust REAL DEFAULT -1.0,
                                        red INTEGER DEFAULT -1, 
                                        green INTEGER DEFAULT -1,
                                        blue INTEGER DEFAULT -1,
                                        motion INTEGER DEFAULT -1,
                                        time INTEGER DEFAULT -1,
                                        FOREIGN KEY (node_id) REFERENCES Registration (node_id) ON DELETE CASCADE ON UPDATE CASCADE""")

    db.createTable("EnergyMonitor", """ id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        node_id INTEGER,
                                        voltage REAL DEFAULT -1.0,
                                        current REAL DEFAULT -1.0,
                                        active_power REAL DEFAULT -1.0,
                                        power_factor REAL DEFAULT -1.0,
                                        frequency REAL DEFAULT -1.0,
                                        active_energy REAL DEFAULT -1.0,
                                        time INTEGER DEFAULT -1, 
                                        FOREIGN KEY (node_id) REFERENCES Registration (node_id) ON DELETE CASCADE ON UPDATE CASCADE""")

    db.createTable("ActuatorMonitor", """   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            node_id INTEGER,
                                            current_value REAL DEFAULT -1.0,
                                            mode TEXT(10) DEFAULT "Unknown",
                                            state INTEGER DEFAULT -1,
                                            time INTEGER DEFAULT -1,
                                            FOREIGN KEY (node_id) REFERENCES Registration (node_id) ON DELETE CASCADE ON UPDATE CASCADE""")

    db.createTable("ActuatorControl", """   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            node_id INTEGER,
                                            setpoint REAL DEFAULT -1.0,
                                            mode TEXT(10) DEFAULT "Unknown",
                                            start_time INTEGER DEFAULT -1,
                                            end_time INTEGER DEFAULT -1,
                                            state INTEGER DEFAULT -1,
                                            time INTEGER DEFAULT -1,
                                            FOREIGN KEY (node_id) REFERENCES Registration (node_id) ON DELETE CASCADE ON UPDATE CASCADE""")

def createDatabaseSchedule():
    db = SqliteDAO(location)
    items = db.__do__(f"SELECT * FROM Registration")
    date = datetime.datetime.utcfromtimestamp(now())
    newFileName = f"./data/data_{date.month}_{date.year}.db"
    os.rename("./data/data.db", newFileName)
    createDatabase()
    db = SqliteDAO(location)
    for item in items:
        db.insertOneRecord(
            "Registration", ["node_id","function","sync_state","protocol","time"], item)

def RecordMaker(data) -> dict:
    record = {
        "fields": None,
        "values": [],
    }
    record['fields'] = list(my_dict.keys())
    data = []
    for key in record['fields']:
        data.append(data[key])

    record['values'] = tuple(data)
    return record
    
    