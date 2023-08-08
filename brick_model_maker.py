from rdflib import RDFS, RDF, Namespace, Graph, URIRef, XSD, SKOS, Literal
# import brickschema

g = Graph()
BRICK = Namespace('https://brickschema.org/schema/1.3/Brick#')
#BF = Namespace('https://brickschema.org/schema/1.3/BrickFrame#')
EX = Namespace('http://example.com#')

g.bind('ex', EX)
g.bind('brick', BRICK)
g.bind('rdfs', RDFS)
g.bind('rdf', RDF)
g.bind('xsd', XSD)
g.bind('skos', SKOS)
g.bind('literal', Literal)

#Creating Building and 2 Rooms
building = (EX['Building-1'], RDF['type'], BRICK['Building'])
g.add(building)

BIMA_room = (EX['RoomBIMA'], RDF['type'], BRICK['Exercise_Room'])
BIMA_room_building = (EX['RoomBIMA'], BRICK['isLocatedIn'], EX['Building-1'])
g.add(BIMA_room)
g.add(BIMA_room_building)

BIMB_room = (EX['RoomBIMB'], RDF['type'], BRICK['Library'])
BIMB_room_building = (EX['RoomBIMB'], BRICK['isLocatedIn'], EX['Building-1'])
g.add(BIMB_room)
g.add(BIMB_room_building)


#Ceating Equipment
#Creating VAV Located in RoomA
VAVA = (EX['VAV-A'], RDF['type'], BRICK['VAV'])
VAVA_BIMA = (EX['VAV-A'], BRICK['isLocatedIn'], EX['RoomBIMA'])
g.add(VAVA)
g.add(VAVA_BIMA)

#Creating VAV Located in RoomB
VAVB = (EX['VAV-B'], RDF['type'], BRICK['VAV'])
VAVB_BIMB = (EX['VAV-B'], BRICK['isLocatedIn'], EX['RoomBIMB'])
g.add(VAVB)
g.add(VAVB_BIMB)

#Creating AHU that feeds VAV's in RoomA and RoomB
AHU = (EX['AHU-AB'], RDF['type'], BRICK['AHU'])
AHU_VAVA = (EX['AHU-AB'], BRICK['feeds'], EX['VAV-A'])
AHU_VAVB = (EX['AHU-AB'], BRICK['feeds'], EX['VAV-B'])
g.add(AHU)
g.add(AHU_VAVA)
g.add(AHU_VAVB)


#Creating Zones
g.add((EX['Zone-A'], RDF['type'], BRICK['HVAC_Zone']))
g.add((EX['VAV-A'], BRICK['feeds'], EX['Zone-A']))

g.add((EX['Zone-B'], RDF['type'], BRICK['HVAC_Zone']))
g.add((EX['VAV-B'], BRICK['feeds'], EX['Zone-B']))


#Creating Measuring Equipment and linking to HVAC equipment and Zones
g.add((EX['SensorA'], RDF['type'], BRICK['Temperature_Sensor']))
g.add((EX['SensorA'], BRICK['isPointOf'], EX['VAV-A']))
g.add((EX['SensorA'], BRICK['isLocatedIn'], EX['Zone-A']))

g.add((EX['SensorB'], RDF['type'], BRICK['Temperature_Sensor']))
g.add((EX['SensorB'], BRICK['isPointOf'], EX['VAV-B']))
g.add((EX['SensorB'], BRICK['isLocatedIn'], EX['Zone-B']))

#Linking Sensors To Databases
g.add((EX['SensorA'], BRICK['hasTimeseriesReference'], Literal("csv_data/SensorA.csv")))
g.add((EX['SensorB'], BRICK['hasTimeseriesReference'], Literal("csv_data/SensorB.csv")))


g.serialize(destination='2RoomsFacility.ttl', format='turtle')
print('Process Done')