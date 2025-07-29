import click
from .core import get_moon_info, get_next_lunar_phases
from .moon_tools import show_moon_chart

@click.group()
def cli():
    """astro_what CLI — lunar data at your fingertips 🌙"""
    pass

@cli.command()
@click.option('--date', default="2025-06-23", help="Date in YYYY-MM-DD format")
@click.option('--hour', default=6, help="Hour (UTC time, 0–23)")
@click.option('--lat', default=12.2958, help="Latitude of location (e.g. 12.2958 for Mysuru)")
@click.option('--lon', default=76.6394, help="Longitude of location (e.g. 76.6394 for Mysuru)")
def moon(date, hour, lat, lon):
    """Show moon position and phase info for a given date and time."""
    data = get_moon_info(date, hour, lat, lon)
    click.echo(f"🌕 Moon info for {date} at {hour}:00 UTC")
    click.echo(f"Phase       : {data['phase']}")
    click.echo(f"Illumination: {data['illumination']}%")
    click.echo(f"Altitude    : {data['altitude']}°")
    click.echo(f"Azimuth     : {data['azimuth']}°")

@cli.command()
@click.option('--from-date', default="2025-06-23", help="Start date (YYYY-MM-DD)")
@click.option('--days', default=7, help="Number of days to scan ahead for moon phases")
def phases(from_date, days):
    """List upcoming moon phase changes."""
    events = get_next_lunar_phases(from_date, days)
    click.echo(f"🌗 Lunar phases from {from_date} for {days} days:")
    for e in events:
        click.echo(f"{e['phase']:12} → {e['timestamp']} UTC")


@cli.command()
@click.option('--date', default="2025-06-23", help="Date in YYYY-MM-DD")
@click.option('--hour', default=6, help="Hour (UTC)")
@click.option('--lat', default=12.2958, help="Latitude")
@click.option('--lon', default=76.6394, help="Longitude")
def chart(date, hour, lat, lon):
    """Render a polar chart of moon location."""
    click.echo(f"🌔 Rendering moon chart for {date} at {hour}:00 UTC...")
    show_moon_chart(date_str=date, hour=hour, lat=lat, lon=lon)
