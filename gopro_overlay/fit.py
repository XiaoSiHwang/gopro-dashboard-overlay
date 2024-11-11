from pathlib import Path

import fitdecode

from gopro_overlay.entry import Entry
from gopro_overlay.gpmf import GPSFix
from gopro_overlay.point import Point
from gopro_overlay.timeseries import Timeseries


def garmin_to_gps(v):
    return v / ((2 ** 32) / 360)


interpret = {
    "position_lat": lambda f, u: {"lat": garmin_to_gps(f.value)},
    "position_long": lambda f, u: {"lon": garmin_to_gps(f.value)},
    "distance": lambda f, u: {"odo": u.Quantity(f.value, u.m)},
    "altitude": lambda f, u: {"alt": u.Quantity(f.value, u.m)},
    "enhanced_altitude": lambda f, u: {"alt": u.Quantity(f.value, u.m)},
    "speed": lambda f, u: {"speed": u.Quantity(f.value, u.mps)},
    "enhanced_speed": lambda f, u: {"speed": u.Quantity(f.value, u.mps)},
    "heart_rate": lambda f, u: {"hr": u.Quantity(f.value, u.bpm)},
    "cadence": lambda f, u: {"cad": u.Quantity(f.value, u.rpm)},
    "temperature": lambda f, u: {"atemp": u.Quantity(f.value, u.degC)},
    "gps_accuracy": lambda f, u: {"dop": u.Quantity(f.value)},
    "power": lambda f, u: {"power": u.Quantity(f.value, u.watt)},
    "grade": lambda f, u: {"grad": u.Quantity(f.value)},
    "Sdps": lambda f, u: {"sdps": u.Quantity(f.value, u.cm)},
    #### Stryd Sensor Parameters
    "Power": lambda f, u: {"stryd_power": u.Quantity(f.value, u.watt)},
    "Form Power": lambda f, u: {"stryd_form_power": u.Quantity(f.value, u.watt)},
    "Leg Spring Stiffness": lambda f, u: {"stryd_lss": u.Quantity(f.value, u.lss)},
    "Cadence":  lambda f, u: {"stryd_cadence": u.Quantity(f.value, u.rpm)},
    "Ground Time":  lambda f, u: {"stryd_gct": u.Quantity(f.value, u.ms)},
    "Vertical Oscillation":  lambda f, u: {"stryd_vo": u.Quantity(f.value, u.cm)},
    "Air Power":  lambda f, u: {"stryd_airpower": u.Quantity(f.value, u.watt)},
    "Stryd Humidity":  lambda f, u: {"stryd_humidity": u.Quantity(f.value, u.percent)},
    "Stryd Temperature":  lambda f, u: {"stryd_temp": u.Quantity(f.value, u.degC)},
    "Impact Loading Rate":  lambda f, u: {"stryd_ilr": u.Quantity(f.value, u.ilr)},
}


def load_timeseries(filepath: Path, units):
    ts = Timeseries()

    with fitdecode.FitReader(filepath) as ff:
        for frame in (f for f in ff if f.frame_type == fitdecode.FIT_FRAME_DATA and f.name == 'record'):
            entry = None
            items = {}

            for field in frame.fields:
                if field.name == "timestamp":
                    # we should set the gps fix or Journey.accept() will skip the point:
                    entry = Entry(
                        dt=field.value,
                        gpsfix=GPSFix.LOCK_3D.value
                    )
                else:
                    if field.name in interpret and field.value is not None:
                        items.update(**interpret[field.name](field, units))

            if "lat" in items and "lon" in items:
                items["point"] = Point(lat=items["lat"], lon=items["lon"])
                del (items["lat"])
                del (items["lon"])

            # only use fit data items that have lat/lon
            if "point" in items:
                entry.update(**items)
                ts.add(entry)

    return ts
