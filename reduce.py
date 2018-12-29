#!/usr/bin/env python3

import gpxpy


# parse GPX
gpx_file = open('test/RunnerUp_01.gpx', 'r')
gpx = gpxpy.parse(gpx_file)

# simplify
gpx.smooth()
gpx.simplify()

# save
print(gpx.to_xml())
