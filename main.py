import simpy #time environment

#self developed tools to simulate temperature and interact with database
from helper import create_table, query, sensor, reader, chekup_process, database_maker, drop_all_tables, get_facility_location

class System(object):
    """Purpose of this class is to store all data that is required to link processes together"""
    def __init__(self, env):
        self.env = env
        self.links = {}
        self.tables = []
        self.location_temperature = 0

    def update_links(self, data):
        """Rewrites dictionary of links"""
        self.links = data

    def give_links(self):
        """Returns dictionary with all links"""
        return self.links
    
    def add_tables(self, table):
        self.tables.append(table)

    def give_tables(self):
        return self.tables
    
    def give_location_temperature(self):
        return self.location_temperature


#System logic. Execution time is limited by 10 time entities. 
env = simpy.Environment() #Creating timeline
system = System(env) #Creating linking class

env.process(query(env, system)) #First step is to query Brick model and extract all sensors
env.process(drop_all_tables(env, system)) #Tables are supposed to be droped after every start of simulation
env.process(get_facility_location(env, system))

env.process(database_maker(env, system))
# env.process(checkup_process(env, system)) #Checking process. Prints current time in a system
env.process(sensor(env, system)) #Process of streaming data and writing data to databases

# env.process(testing_query(env, system)) 
env.process(reader(env, system)) #Process of reading data from databases
env.run(until=10) #Setting living time of system