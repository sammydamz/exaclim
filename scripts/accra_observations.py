"""Write matched hourly observations and archived forecasts to stdout."""
import csv
import json
import sys
from datetime import date, timedelta
from io import StringIO
from urllib.parse import urlencode
from urllib.request import urlopen

start, end = date(2025, 2, 1), date(2025, 2, 28)
site = {"latitude": 5.6037, "longitude": -0.187}
variables = ["temperature_2m", "relative_humidity_2m"]
query = dict(site, start_date=start, end_date=end, models="icon_global",
             hourly=",".join(f"{v}_previous_day{d}" for d in (1, 2) for v in variables))
forecast_url = "https://previous-runs-api.open-meteo.com/v1/forecast?" + urlencode(query)
stop = end + timedelta(days=1)
station_query = dict(station="DGAA", data=["tmpc", "relh"], year1=start.year, month1=start.month,
                     day1=start.day, year2=stop.year, month2=stop.month, day2=stop.day,
                     tz="Etc/UTC", format="onlycomma", latlon="yes", report_type=[3, 4])
station_url = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?" + urlencode(station_query, doseq=True)
with urlopen(forecast_url, timeout=60) as response:
    forecast = json.load(response)
with urlopen(station_url, timeout=60) as response:
    records = csv.DictReader(StringIO(response.read().decode()))
    observed = {}
    for row in records:
        if row["station"] != "DGAA" or not row["valid"].endswith(":00"):
            continue
        try:
            pair = float(row["tmpc"]), float(row["relh"])
        except ValueError:
            continue
        key = row["valid"].replace(" ", "T")
        if key in observed and observed[key] != pair:
            observed[key] = None
        else:
            observed[key] = pair
hours = forecast["hourly"]
writer = csv.writer(sys.stdout)
writer.writerow(["valid_utc","lead_days","obs_c","obs_rh","fc_c","fc_rh"])
for i, time in enumerate(hours["time"]):
    for day in (1, 2):
        prediction = [hours[f"{v}_previous_day{day}"][i] for v in variables]
        if observed.get(time) and None not in prediction:
            writer.writerow([time,day,*observed[time],*prediction])
