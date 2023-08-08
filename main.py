#Importing modules
import streamlit as st
import pandas as pd
import numpy as np

#importing helping tools
from helper import query, graph_builder, get_coordinates, find_closest_city

st.set_page_config(page_title="Temperature Sensor Visualisation", 
                   page_icon = "👹", 
                   layout="wide")

@st.cache_data()
def get_data() -> pd.DataFrame:
    return pd.read_csv("ashrae_db2.01_customized.csv")

#Defining session
session = st.session_state

#Defining main parameters
session["IFC_loaded"] = False
session["Brick_loaded"] = False
session["Select_location_manually"] = True
session["Closest_city_name"] = None
session["IFC_file"] = None
session["Brick_model"] = None
session["Dict_of_sensors"] = {}
session["Coordinates"] = []
session["City_identified"] = False

def change_select_location_manually():
    session["Select_location_manually"] = False

def change_city_identified():
    session["City_identified"] = True

comfort_df = get_data() #ASHRAE Thermal comfort database

st.title("Temperature Heatmap")
place_holder = st.empty()

# Loading files with data
st.subheader("Put Brick model and IFC")
file1, file2 = st.columns(2)
with file1:
    session["Brick_model"] = st.file_uploader("Load Brick Model")
    if session["Brick_model"]:
        session["Brick_loaded"] = True
        sensors = query(session["Brick_model"])

        session["Dict_of_sensors"] = sensors
        st.info(f"Links to sensor's data found in amount of {len(sensors)}")
        st.write("Sensors found: ", sensors)

with file2:
    session["IFC_file"] = st.file_uploader("Load IFC", on_change=change_select_location_manually)
    if session["IFC_file"]:
        session["Coordinates"] = get_coordinates(session["IFC_file"])
        session["IFC_loaded"] = True

        st.write("Coordinates from IFC", session["Coordinates"])
        session["Closest_city_name"] = find_closest_city(comfort_df, session["Coordinates"])

        st.warning(f"Geographically closest city is: {session['Closest_city_name']}")

#Working with Thermal comfort database
st.subheader("Select Values in Comfort database")
fig_col1, fig_col2 = st.columns(2)
with fig_col1:
    if session["IFC_loaded"] == False:   
        cities = comfort_df["City"].unique().astype(str)
        cities = np.sort(cities[np.where(cities != "nan")])
        city_option = st.selectbox("Selecting Location", cities, on_change=change_city_identified)
        
    else:
        st.info('Location was set from IFC', icon="ℹ️")
        city_option = session["Closest_city_name"]

with fig_col2:
    type_of_facility = comfort_df[comfort_df["City"] == city_option]["Building type"].unique()
    facility_option = st.selectbox("Select Type of Facility", type_of_facility)

result_df = comfort_df[comfort_df["City"] == city_option]
result_df = result_df[result_df["Building type"] == facility_option]
ref_value = np.round(np.nanmean(result_df["SET"]), 2)

if session["IFC_file"]:
    session["City_identified"] = True

if session["City_identified"] == True:
    st.warning(f"Optimal value for location {session['Closest_city_name']} is {ref_value}")

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#Building Graph
place_holder = st.empty()

st.write(session)

if st.button("Push me to build graph"):
    with place_holder.container():
        from_query = list(sensors.values())
        fig = graph_builder(from_query[0], from_query[1], ref_value)
        st.plotly_chart(fig, use_container_width=True)