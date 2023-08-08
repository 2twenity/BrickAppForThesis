import pandas as pd
import random
from datetime import datetime, timedelta

#format of data in columns:
# 1) Datetime value(Every 15 mins for 1 month)
# 2) Temperature value
#File is supposed to be called like a sensor

step = timedelta(minutes=15)
starting_date = datetime.now()

data = {"Datetime":[], "Temperature":[]}

for _ in range(2200):
    starting_date += step
    data["Datetime"].append(starting_date)
    data["Temperature"].append(random.randint(20, 45))

sensor_df = pd.DataFrame(data)

sensor_df.to_csv("SensorA.csv")