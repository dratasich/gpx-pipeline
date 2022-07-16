#!/usr/bin/env python3

# intro and code (parse gpx, plot) from
# https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d

import gpxpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from simplification.cutil import simplify_coords
from pykalman import KalmanFilter


# parse GPX
gpx_file = open("test/RunnerUp_01.gpx", "r")
gpx = gpxpy.parse(gpx_file)
data = gpx.tracks[0].segments[0].points


# GPX to pandas data frame
df = pd.DataFrame(columns=["lon", "lat", "alt", "time"])
for segment in gpx.tracks[0].segments:
    for point in segment.points:
        df = df.append(
            {
                "lon": point.longitude,
                "lat": point.latitude,
                "alt": point.elevation,
                "time": point.time,
            },
            ignore_index=True,
        )

start = df.iloc[0]
finish = df.iloc[-1]


# post-processing
stages = []
stages.append(df)


def moving_averaging(df, window=10):
    return df[["lat", "lon", "alt"]].rolling(window, win_type="hamming").mean().dropna()


def kalman_filter_add_v(df):
    # calculate v_lat and v_lon for each coordinate
    v_lat = [0]
    v_lon = [0]
    for i in range(len(df) - 1):
        lon1 = df["lon"].iloc[i]
        lat1 = df["lat"].iloc[i]
        lon2 = df["lon"].iloc[i + 1]
        lat2 = df["lat"].iloc[i + 1]
        dt = (df["time"].iloc[i + 1] - df["time"].iloc[i]).seconds
        if dt == 0:
            dt = 0.1
        vlat = (lat2 - lat1) / dt
        vlon = (lon2 - lon1) / dt
        v_lat.append(vlat)
        v_lon.append(vlon)
    df.loc[:, "v_lon"] = pd.Series(v_lon, index=df.index)
    df.loc[:, "v_lat"] = pd.Series(v_lat, index=df.index)
    return df


def kalman_filter(df):
    # KF parameters
    t = 2  # seconds
    # state is [lon, lat, v_lon, v_lat]
    transition_matrix = [[1, 0, t, 0], [0, 1, 0, t], [0, 0, 1, 0], [0, 0, 0, 1]]
    transition_offset = [0, 0, 0, 0]
    observation_matrix = np.eye(4)
    observation_offset = [0, 0, 0, 0]
    transition_covariance = np.eye(4) * 0.00001
    observation_covariance = np.eye(4) * 0.001
    initial_state_mean = df[["lon", "lat", "v_lon", "v_lat"]].iloc[0]
    initial_state_covariance = np.eye(4)
    # KF init
    kf = KalmanFilter(
        transition_matrix,
        observation_matrix,
        transition_covariance,
        observation_covariance,
        transition_offset,
        observation_offset,
        initial_state_mean,
        initial_state_covariance,
    )
    observations = df[["lon", "lat", "v_lon", "v_lat"]].values
    # filter
    state_mean, _ = kf.filter(observations)
    df = pd.DataFrame(state_mean, columns=["lon", "lat", "v_lon", "v_lat"])
    return df


def ramer_douglas_peucker(df, epsilon=0.00005):
    arr = df[["lon", "lat"]].values.copy(order="C")
    df = pd.DataFrame(simplify_coords(arr, epsilon), columns=["lon", "lat"])
    return df


df = moving_averaging(df)
# df = kalman_filter_add_v(df)
# df = kalman_filter(df)
stages.append(df)
df = ramer_douglas_peucker(df)
stages.append(df)


# convert back to gpx
gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)
for i in range(len(df)):
    lon, lat = df[["lon", "lat"]].iloc[i]
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon))

# save
with open("test/RunnerUp_01-plot.gpx", "w") as f:
    f.write(gpx.to_xml())


# plot
for i, df in enumerate(stages):
    print(f"Plot {len(df)} points for stage {i} ...")
    plt.plot(df["lon"], df["lat"], marker=".", label=f"stage {i}")

plt.plot(start["lon"], start["lat"], marker="o", color="red")
plt.plot(finish["lon"], finish["lat"], marker="o", color="green")

plt.legend()

print("Press 'q' to quit or close the figure.")
plt.show()
