import matplotlib.pyplot as plt
from .core import get_moon_info  # Note the dot for relative import
import math

def show_moon_chart(date_str="2025-06-23", hour=6, lat=12.2958, lon=76.6394):
    data = get_moon_info(date_str, hour, lat, lon)
    r = 90 - data["altitude"]
    theta = math.radians(data["azimuth"])

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.scatter(theta, r, c='silver', s=200, edgecolors='black', label="Moon")
    ax.set_rlim(0, 90)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(225)

    title = f"{data['phase']}, {data['illumination']}% illuminated\n{date_str}"
    ax.set_title(title, fontsize=12)
    ax.legend()
    plt.show()
