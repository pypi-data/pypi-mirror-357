 # 🌙 astro_what

A Python command-line tool to explore moon phases, positions, and lunar events — directly from your terminal. Built using Skyfield and Click, it’s perfect for hobbyist astronomers, students, and night-sky enthusiasts.

## Features

- Get real-time moon phase and illumination data
- Forecast upcoming lunar phase transitions
- Visualize the moon’s position using polar charts
- Fully offline-friendly after installation

## Installation

pip install astro-what

## Usage in CLI 
- astro moon --date 2025-06-23
- astro phases --days 5
- astro chart --date 2025-06-23

##🧰 Available Functions in astro_what

The following functions are accessible when using astro_what as a Python module:

From astro_what.core:

- get_moon_info(date_str, hour, lat, lon) Returns a dictionary containing:

		- Moon phase (e.g. “Waxing Gibbous”)

		- Illumination percentage

		- Altitude and azimuth in degrees

- get_next_lunar_phases(from_date, days) Returns a list of upcoming lunar phase transitions within a given timeframe.

From astro_what.moon_tools:
- show_moon_chart(date_str, hour, lat, lon) Opens a polar plot showing the Moon’s position relative to the horizon — useful for visualizing where to look in the sky.

🌙 Example: Get Moon Information

		from astro_what.core import get_moon_info

		moon = get_moon_info(date_str="2025-06-23", hour=6, lat=12.2958, lon=76.6394)

		print(f"Phase       : {moon['phase']}")
		print(f"Illumination: {moon['illumination']}%")
		print(f"Altitude    : {moon['altitude']}°")
		print(f"Azimuth     : {moon['azimuth']}°")

🌗 Example: Get Upcoming Lunar Phases

		from astro_what.core import get_next_lunar_phases

		phases = get_next_lunar_phases(from_date="2025-06-23", days=5)
		for p in phases:
		    print(f"{p['phase']} → {p['timestamp']} UTC")

📈 Example: Plot Moon Position Chart

		from astro_what.moon_tools import show_moon_chart

		show_moon_chart(date_str="2025-06-23", hour=6, lat=12.2958, lon=76.6394)
