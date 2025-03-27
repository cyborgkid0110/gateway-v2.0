import calendar
import datetime
from multiprocessing import Process
from src.gateway_server import gw2sv
from src.things_gateway import btmesh_app

class MultiTasks():
    def __init__(self, tasks):
        self.tasks = tasks
    
    def start(self):
        self.processes = []
        for task in self.tasks:
            self.processes.append(Process(target=task))
        for process in self.processes:
            process.start()
    
    def restart(self):
        for process in self.processes:
            process.terminate()

        for process in self.processes:
            process.join()
            
        self.start()

tasks = []
tasks.append(gw2sv.main)
tasks.append(btmesh_app.main)

multi_tasks = MultiTasks(tasks)
multi_tasks.start()

# Read the time to use for automatically creating a new database every month
timestamp = calendar.timegm(datetime.datetime.utcnow().utctimetuple())+7*3600
date = datetime.datetime.utcfromtimestamp(timestamp)
preMonth = date.month
while True:
    timestamp = calendar.timegm(datetime.datetime.utcnow().utctimetuple())+7*3600
    date = datetime.datetime.utcfromtimestamp(timestamp)
    newMonth = date.month 
    if (newMonth != preMonth):
        multi_tasks.restart()
        preMonth = newMonth