#!/usr/bin/env python3

# intro and code (parse gpx, plot) from
# https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d

import gpxpy
import pandas as pd
import matplotlib.pyplot as plt


# parse GPX
gpx_file = open('test/RunnerUp_01.gpx', 'r')
gpx = gpxpy.parse(gpx_file)
data = gpx.tracks[0].segments[0].points


# GPX to pandas data frame
df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
for segment in gpx.tracks[0].segments:
    for point in segment.points:
        df = df.append({'lon': point.longitude, 'lat' : point.latitude,
                        'alt' : point.elevation, 'time' : point.time},
                       ignore_index=True)


# plot
start = df.iloc[0]
finish = df.iloc[-1]

print(f"Plot {len(df)} points ...")
plt.plot(df['lon'], df['lat'])
plt.plot(start['lon'], start['lat'], marker='o', color='red')
plt.plot(finish['lon'], finish['lat'], marker='o', color='green')
print("Press 'q' to quit or close the figure.")
plt.show()
