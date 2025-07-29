from skyfield.api import load, wgs84
from numpy import arccos, degrees
from skyfield import almanac

def get_moon_info(date_str="2025-06-23", hour=18, lat=12.2958, lon=76.6394):
    ts = load.timescale()
    eph = load('de421.bsp')

    y, m, d = map(int, date_str.split('-'))
    t = ts.utc(y, m, d, hour)

    observer = eph['earth'] + wgs84.latlon(lat, lon)
    sun, moon = eph['sun'], eph['moon']

    sun_vec = observer.at(t).observe(sun).apparent().position.au
    moon_vec = observer.at(t).observe(moon).apparent().position.au

    dot = sum(s * m for s, m in zip(sun_vec, moon_vec))
    mag_sun = sum(s**2 for s in sun_vec)**0.5
    mag_moon = sum(m**2 for m in moon_vec)**0.5
    cos_theta = dot / (mag_sun * mag_moon)
    phase_angle = degrees(arccos(cos_theta))
    illumination = round((1 + cos_theta) / 2 * 100, 2)

    # Phase classification
    angle = (phase_angle + 180) % 360
    if angle < 45:
        phase = "New Moon 🌑"
    elif angle < 90:
        phase = "First Quarter 🌓"
    elif angle < 135:
        phase = "Waxing Gibbous 🌔"
    elif angle < 225:
        phase = "Full Moon 🌕"
    elif angle < 270:
        phase = "Last Quarter 🌗"
    else:
        phase = "Waning Crescent 🌘"

    alt, az, _ = observer.at(t).observe(moon).apparent().altaz()

    return {
        "phase": phase,
        "illumination": illumination,
        "altitude": round(alt.degrees, 2),
        "azimuth": round(az.degrees, 2),
        "timestamp": t.utc_iso()
    }



def get_next_lunar_phases(start_date="2025-06-23", days_ahead=7):
    ts = load.timescale()
    eph = load('de421.bsp')

    y, m, d = map(int, start_date.split("-"))
    t0 = ts.utc(y, m, d)
    t1 = ts.utc(y, m, d + days_ahead)

    phase_func = almanac.moon_phases(eph)
    times, phases = almanac.find_discrete(t0, t1, phase_func)

    phase_names = ["New Moon 🌑", "First Quarter 🌓", "Full Moon 🌕", "Last Quarter 🌗"]
    results = []
    for t, p in zip(times, phases):
        results.append({
            "phase": phase_names[p],
            "timestamp": t.utc_datetime()
        })
    return results



