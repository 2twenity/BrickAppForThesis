import pandas

def temperature_according_to_location():
    df = pandas.read_csv("ashrae_db2.01.csv")

    location = "Lisbon"

    all_set = []

    for i in df.itertuples():
        if i.City == location:
            if isinstance(i.SET, float):
                all_set.append(i.SET)

    return all_set[0]

# print(list(df.columns.values)) #Printing All columns

# df = pandas.read_csv("ashrae_db2.01.csv")
# print(df["Country"].unique())
# print("---------------------")
# 
# print(df["City"].unique())

# print(df["Air temperature (C)"].unique())