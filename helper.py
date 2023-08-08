from rdflib import Graph #to query Brick model
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import ifcopenshell

def query(graph_name):

    g = Graph()
    data = g.parse(graph_name, format='turtle')

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
    
    return extract_sensors(data)

def graph_builder(path_1, path_2, ref_value):
    SensorA_df = pd.read_csv(f"{path_1}")
    SensorB_df = pd.read_csv(f"{path_2}")

    # Changing datatype to datetime
    SensorA_df["Datetime"] = pd.to_datetime(SensorA_df["Datetime"])
    SensorB_df["Datetime"] = pd.to_datetime(SensorB_df["Datetime"])

    Sensors = ["SensorA", "SensorB"]

    DictA = {"day": [], "avg_temp_A": []}
    minimal_day, maximal_day = min(SensorA_df["Datetime"].dt.day), max(SensorA_df["Datetime"].dt.day)

    for i in range(minimal_day, maximal_day + 1):
        temp_array = SensorA_df["Temperature"][SensorA_df["Datetime"].dt.day == i]
        avg = np.round(np.mean(temp_array), 2)
        DictA["day"].append(i)
        DictA["avg_temp_A"].append(avg)

    DictB = {"day": [], "avg_temp_B": []}
    minimal_day, maximal_day = min(SensorB_df["Datetime"].dt.day), max(SensorB_df["Datetime"].dt.day)

    for i in range(minimal_day, maximal_day + 1):
        temp_array = SensorB_df["Temperature"][SensorB_df["Datetime"].dt.day == i]
        avg = np.round(np.mean(temp_array), 2)
        DictB["day"].append(i)
        DictB["avg_temp_B"].append(avg)

    day_sensorA_df = pd.DataFrame(DictA).set_index(["day"])
    day_sensorB_df = pd.DataFrame(DictB).set_index(["day"])

    res = day_sensorA_df.join(day_sensorB_df)

    x = list(range(1, len(res)+1))
    y = Sensors

    array_a = np.array(res["avg_temp_A"])
    array_b = np.array(res["avg_temp_B"])

    z = np.array([array_a, array_b])

    #calculating temperature range
    #maximal = np.max(z["avg_temp_A"])
    maximal_temp = np.nanmax(z)
    minimal_temp = np.nanmin(z)
    print("Minimal temp: ", maximal_temp)
    print("Maximal temp: ", minimal_temp)
    print("Value from DB: ", ref_value)
    calc_value = np.round((ref_value - minimal_temp)/ (maximal_temp - minimal_temp), 2)
    print("Calculated value: ", calc_value)

    if np.isnan(calc_value):
        fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y,
                                        colorscale = [[0, "blue"],
                                                    [1.0, "red"]]))
    else:
        fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y,
                                        colorscale = [[0, "blue"],
                                                    [calc_value, 'yellow'],
                                                    [1.0, "red"]]))

    fig.update_layout(
        title='Avg Temperature During the Day',
        xaxis_nticks=36)
    
    return fig

def get_coordinates(ifc_path):
    def dms2dd(d, m, s):
        return d + m/60 + s/3600

    ifc = ifcopenshell.file.from_string(ifc_path.getvalue().decode("utf-8"))
    coordinates = ifc.by_type('IFCSITE')
    case = []
    for each in coordinates[0]:
        if type(each) is tuple:
            case.append(each)

    coordinates = []
    for each in case:
        d, m, s = each[0], each[1], each[2]
        coordinates.append(round(dms2dd(d, m, s), 6))
    return coordinates

def find_closest_city(comfort_df, ifc_coordinates):
    coord_df = comfort_df[["Coordinates_lat", "Coordinates_long"]].drop_duplicates()
    coord_arr = np.array((coord_df["Coordinates_lat"].astype(float), coord_df["Coordinates_long"].astype(float)))

    cities_arr = np.array(comfort_df["City"].drop_duplicates())
    point_lat1 = np.deg2rad(np.array(coord_df["Coordinates_lat"].astype(float)))
    point_long1 = np.deg2rad(np.array(coord_df["Coordinates_long"].astype(float)))

    point_lat2 = np.deg2rad(ifc_coordinates[0])
    point_long2 = np.deg2rad(ifc_coordinates[1])

    #coord_arr[0] = coord_arr[0].astype(str)

    dlat = point_lat1 - point_lat2
    dlon = point_long1 - point_long2

    a = np.power(np.sin(dlat / 2), 2) + np.cos(point_lat1) * np.cos(point_lat2) * np.power(np.sin(dlon / 2), 2)

    c = 2 * np.sqrt(np.arcsin(a))
    r = 6371

    res = r*c
    return cities_arr[np.argmin(res)]