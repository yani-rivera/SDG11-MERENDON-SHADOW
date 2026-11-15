"""Sun altitude and azimuth (NOAA approximation)."""
import math
from datetime import datetime, timedelta, timezone

def sun_position(lat, lon, when_utc):
    d = when_utc
    jd = (d - datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds()/86400 + 2451545.0
    T = (jd - 2451545.0)/36525
    L0 = (280.46646 + T*(36000.76983 + T*0.0003032)) % 360
    M = 357.52911 + T*(35999.05029 - 0.0001537*T)
    e = 0.016708634 - T*(0.000042037 + 0.0000001267*T)
    Mr = math.radians(M)
    C = math.sin(Mr)*(1.914602 - T*(0.004817+0.000014*T)) + math.sin(2*Mr)*(0.019993-0.000101*T) + math.sin(3*Mr)*0.000289
    lam = L0 + C - 0.00569 - 0.00478*math.sin(math.radians(125.04-1934.136*T))
    eps0 = 23 + (26 + (21.448 - T*(46.815 + T*(0.00059 - T*0.001813)))/60)/60
    eps = eps0 + 0.00256*math.cos(math.radians(125.04-1934.136*T))
    decl = math.degrees(math.asin(math.sin(math.radians(eps))*math.sin(math.radians(lam))))
    y = math.tan(math.radians(eps/2))**2
    L0r = math.radians(L0)
    eot = 4*math.degrees(y*math.sin(2*L0r) - 2*e*math.sin(Mr) + 4*e*y*math.sin(Mr)*math.cos(2*L0r) - 0.5*y*y*math.sin(4*L0r) - 1.25*e*e*math.sin(2*Mr))
    minutes = d.hour*60 + d.minute + d.second/60
    tst = (minutes + eot + 4*lon) % 1440
    ha = tst/4 - 180
    latr, dr, har = map(math.radians, (lat, decl, ha))
    cosz = math.sin(latr)*math.sin(dr) + math.cos(latr)*math.cos(dr)*math.cos(har)
    alt = 90 - math.degrees(math.acos(cosz))
    az = (math.degrees(math.atan2(math.sin(har), math.cos(har)*math.sin(latr) - math.tan(dr)*math.cos(latr))) + 180) % 360
    return alt, az

if __name__ == "__main__":
    tz = timezone(timedelta(hours=-6))
    for day in (16, 17):
        for hh, mm in [(16,15),(16,30),(16,40),(16,46),(16,47),(16,48),(16,49),(16,50),(16,55),(17,0),(17,10)]:
            t = datetime(2026,11,day,hh,mm,tzinfo=tz).astimezone(timezone.utc)
            alt, az = sun_position(15.5044, -88.025, t)
            print(day, f"{hh}:{mm:02d}", f"alt {alt:5.2f}  az {az:6.2f}  reach of 1500 m relief: {1.5/math.tan(math.radians(alt)):5.1f} km")
