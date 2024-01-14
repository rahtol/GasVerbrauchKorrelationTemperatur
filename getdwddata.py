import csv
import datetime
import io
import zipfile
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import requests
from sortedcontainers import SortedDict

url0 = 'https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate'

urlhourly = '/hourly/air_temperature/recent/stundenwerte_TU_13777_akt.zip'
# urlhourly = '/hourly/air_temperature/recent/stundenwerte_TU_00662_akt.zip'
taghourly = 'produkt_tu_stunde_202'
outfnhourly = 'stundenwerte_TU_13777_akt'
# outfnhourly = 'stundenwerte_TU_00662_akt'

urldaily = '/daily/kl/recent/tageswerte_KL_13777_akt.zip'
tagdaily = 'produkt_klima_tag_202'
outfndaily = 'tageswerte_KL_13777_akt'
tz_berlin = ZoneInfo('Europe/Berlin')
utc = ZoneInfo('UTC')
basetime: datetime = datetime.fromisoformat('1992-01-01T00:00:00Z')

def to_sec(datetimestr: str, tz: ZoneInfo) -> int:
    t: datetime = datetime.strptime(datetimestr, '%Y%m%d%H').astimezone(tz)
    dt: datetime.timedelta = t - basetime
    return int(dt.total_seconds())

def getdwddata(urlpath, outfn, tag):
    r = requests.get(url0 + urlpath)
    assert r.ok
    with open(outfn + '.zip', 'wb') as outf:
        outf.write(r.content)
    with io.BytesIO(r.content) as f:
        with zipfile.ZipFile(f, 'r') as z:
            zdir = z.namelist()
            matches = [match for match in zdir if tag in match]
            assert len(matches) == 1
            with z.open(matches[0]) as zf:
                raw_data = zf.read()
                with open(outfn + '.csv', 'wb') as f2:
                    f2.write(raw_data)
                with io.TextIOWrapper(io.BytesIO(raw_data), newline='') as f3:
                    dict1 = SortedDict()
                    reader = csv.reader(f3, delimiter=';')
                    headers = next(reader)
                    assert 'MESS_DATUM' in headers
                    assert 'TT_TU' in headers;
                    for row in reader:
                        entry = {key: value for key, value in zip(headers, row)}
                        tt_tu: float = float(entry['TT_TU'])
                        if tt_tu != -999:
                            dti: int = to_sec(entry['MESS_DATUM'], tz=utc)
                            dict1[dti] = entry
    return dict1


def getdwddatadaily():
    return getdwddata(urldaily, outfndaily, tagdaily)


def getdwddatahourly():
    return getdwddata(urlhourly, outfnhourly, taghourly)


hourly_data = getdwddatahourly()


def calc_mean_temperature(t0: datetime, t1: datetime):
    n = 0
    sumup = 0.0
    while t0 < t1:
        delta_t_since_basetime: int = int((t0 - basetime).total_seconds())
        entry = hourly_data[delta_t_since_basetime]
        sumup = sumup + float(entry['TT_TU'])
        n = n + 1
#        print(entry['MESS_DATUM'], float(entry['TT_TU']))
        t0 = t0 + timedelta(hours=1)
#    print(f'n={n}, sum={sumup}')
    return sumup / n
