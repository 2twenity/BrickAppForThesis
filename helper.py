#Working with database
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from rdflib import Graph #to query Brick model
import random #to simulate temperature

#Operating on ASHRAE Thermal Comfort Database II
from database_operator import temperature_according_to_location


#Defining function to work with SQLAlchemy
Base = declarative_base()
engine = create_engine("sqlite:///temperature.db")

def create_table(table_name):
    """Return instance of class responsible for
    linking sql table to python environment"""
    class Database(Base):
        __tablename__ = f"{table_name}"

        time = Column("time", Integer, primary_key=True) #Time column
        temperature = Column("temperature", Integer) #Temperature column
    
        def __init__(self, time, temperature):
            self.time = time
            self.temperature = temperature

        def __repr__(self):
            return f"{self.__tablename__}"
        
    return Database 


def query(env, system):
    yield env.timeout(1) #Query is executed as a first process and never repeated

    g = Graph()
    data = g.parse("2RoomsFacility.ttl", format='turtle')

    def extract_sensors(data):
        res = {}
        q = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX brick1: <https://brickschema.org/schema/1.3/Brick#>
        PREFIX ex: <http://example.com#>

        select ?s ?o
        where {
            ?s brick1:hasTimeseriesReference ?o .
        }
        """
        sensors = data.query(q)

        if sensors:
            for sensor in sensors:
                res[sensor[0].__str__()[19:]] = sensor[1].__str__() #!!!!!!!!!!!!!!!HARD CODE!!!!!!!!!!!!!!
        else:
            print("No sensors in the Brick model were found!")
    
        return res
    
    system.update_links(extract_sensors(data)) #Writing data to system class


def sensor(env, system):
    """Simulates temperature deteected by sensors 
    and writes data to sqlite database"""
    while True:
        yield env.timeout(1)
        Session = sessionmaker(bind=engine)
        session = Session()
        for table in system.give_tables():
            value = table (env.now, random.randint(15,25))
            session.add(value)

        session.commit()

def reader(env, system):
    """Reads data from sqlite database"""
    while True:
        yield env.timeout(1)
        for table in system.give_links():
            with engine.connect() as connection:
                result = connection.execute(text(f"select * from {table} ;"))
                last = result.all()[-1]
                last_temp = last[1]

                temp_difference = round(abs(last_temp - system.give_location_temperature()), 2)
                if temp_difference > 4:
                    print(f"!WARNING TEMPERATURE OUT OF RANGE! {table}: {last_temp}, diff: {temp_difference}")
                else:
                    print(f"All good! {table}: {last_temp}, diff: {temp_difference}")

def chekup_process(env, system):
    """Checkin poccess"""
    while True:
        yield env.timeout(9)
        print("Current time is %s" % env.now)
        print("Tables: ", system.give_tables())
        print("Links: ", system.give_links())

def database_maker(env, system):
    """Creates databases. Adds instances of classes to system's tables"""
    yield env.timeout(1)
    for key, value in system.give_links().items():
        table = create_table(key)

        system.add_tables(table)
        print(f"{table} was created and added to system class")

    Base.metadata.create_all(bind=engine)

def drop_all_tables(env, system):
    """Deletes all tables from database. Is supposed to be run as a second"""
    yield env.timeout(1)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    try: #In case there will be no tables in the system
        for name in system.give_links():
            table = metadata.tables[name]
            if table is not None:
                Base.metadata.drop_all(engine, [table], checkfirst=True)
                print("*************")
                print("TABLE DROPPED")
                print("*************")
    except KeyError as Key:
        print("Somethig went wrong with tables in system")


def get_facility_location(env, system):
    yield env.timeout(1)

    temperature_value = temperature_according_to_location()
    system.location_temperature = temperature_value