"""Clock times in the config -> sun position for that minute."""
from datetime import datetime, timedelta, timezone

from .solar import sun_position


def minutes(hhmm):
    """'16:45' -> minutes since midnight."""
    hh, mm = hhmm.split(":")
    return int(hh) * 60 + int(mm)


def label(minute):
    """Minutes since midnight -> '16:45'."""
    return f"{minute // 60}:{minute % 60:02d}"


def sun_for_minute(cfg, minute):
    """Sun altitude and azimuth (degrees) at a local clock minute on the configured date."""
    tz = timezone(timedelta(hours=cfg["sun"]["utc_offset_hours"]))
    y, m, d = map(int, cfg["sun"]["date"].split("-"))
    when = datetime(y, m, d, minute // 60, minute % 60, tzinfo=tz)
    return sun_position(cfg["sun"]["lat"], cfg["sun"]["lon"], when.astimezone(timezone.utc))
