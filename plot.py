#!/usr/bin/env python3

# intro and code (parse gpx, plot) from
# https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d

import gpxpy
import pandas as pd
import matplotlib.pyplot as plt
from simplification.cutil import simplify_coords


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

start = df.iloc[0]
finish = df.iloc[-1]


# post-processing
stages = []
stages.append(df)

def moving_averaging(df, window=10):
    return df.rolling(window, win_type='hamming').mean().dropna()

def ramer_douglas_peucker(df, epsilon=0.00005):
    arr = df[['lat', 'lon']].values.copy(order='C')
    df = pd.DataFrame(simplify_coords(arr, epsilon), columns=['lat', 'lon'])
    return df

df = df.set_index('time')
df = moving_averaging(df)
stages.append(df)
df = ramer_douglas_peucker(df)
stages.append(df)


# plot
for i, df in enumerate(stages):
    print(f"Plot {len(df)} points for stage {i} ...")
    plt.plot(df['lon'], df['lat'], marker='.', label=f"stage {i}")

plt.plot(start['lon'], start['lat'], marker='o', color='red')
plt.plot(finish['lon'], finish['lat'], marker='o', color='green')

plt.legend()

print("Press 'q' to quit or close the figure.")
plt.show()
