import csv
import io
import zipfile
import requests
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from sortedcontainers import SortedDict


class TemperatureTimeCourse(SortedDict):

    url0 = 'https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate'
    basetime: datetime = datetime.fromisoformat('1992-01-01T00:00:00Z')
    utc = ZoneInfo('UTC')
    berlin = ZoneInfo('Europe/Berlin')
    
    def __init__(self, station: str = '13777'):  # by default use station Helmstedt-Emmerstedt
        super().__init__()
        urlhourly = f'/hourly/air_temperature/recent/stundenwerte_TU_{station}_akt.zip'
        taghourly = 'produkt_tu_stunde_202'
        outfnhourly = f'stundenwerte_TU_{station}_akt'
        self.getdwddata(urlhourly, outfnhourly, taghourly)
    
    def measuring_time_to_key(datetimestr: str, tz: ZoneInfo) -> int:
        t: datetime = datetime.strptime(datetimestr, '%Y%m%d%H').astimezone(tz)
        dt: datetime.timedelta = t - TemperatureTimeCourse.basetime
        return int(dt.total_seconds())
    
    def datetime_to_key(t: datetime) -> int:
        key = int((t - TemperatureTimeCourse.basetime).total_seconds())
        return key
    
    def get(self, key) -> float:
        temp: float = float(self[key]['TT_TU'])
        return temp

    def getdwddata(self, urlpath, outfn, tag):
        r = requests.get(TemperatureTimeCourse.url0 + urlpath)
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
                        reader = csv.reader(f3, delimiter=';')
                        headers = next(reader)
                        assert 'MESS_DATUM' in headers
                        assert 'TT_TU' in headers
                        for row in reader:
                            entry = {key: value for key, value in zip(headers, row)}
                            tt_tu: float = float(entry['TT_TU'])
                            if tt_tu != -999:
                                dti: int = TemperatureTimeCourse.measuring_time_to_key(entry['MESS_DATUM'], tz=TemperatureTimeCourse.utc)
                                self[dti] = entry

    def idx_neighbourhood(self, idx: int) -> (int,int):
        if idx == 0:
            ret = (idx, idx+1) # extrapolate at the beginning
        elif idx == len(self):
            ret = (idx-2, idx-1) # extrapolate at the end
        else:
            ret = (idx-1, idx) # interpolate
        return ret

    def __missing__(self, t_key: int):
        idx = self.bisect(t_key)
        (idx0, idx1) = self.idx_neighbourhood(idx)
        t1 = self.bisect_right(t_key)
        (t0, f0) = self.peekitem(idx0)
        (t1, f1) = self.peekitem(idx1)
        temp0 = float(f0['TT_TU'])
        temp1 = float(f1['TT_TU'])
        value = temp0 + ((temp1-temp0)/(t1-t0))*(t_key-t0)
        entry = { 'TT_TU': str(value) }
        self[t_key] = entry
        return entry
    
    def assure_awareness(self, t: datetime) -> datetime:
        if t.tzinfo is None or t.tzinfo.utcoffset(None) is None:
            t_ret = t.astimezone(TemperatureTimeCourse.berlin)
        else:
            t_ret = t
        return t_ret
    
    def calc_mean_temperature(self, t0: datetime, t1: datetime) -> int:
        assert t1 > t0
        t0_aware = self.assure_awareness(t0)
        t1_aware = self.assure_awareness(t1)
        # ensure that start and end timestamp are in the dictionary
        key0 = TemperatureTimeCourse.datetime_to_key(t0_aware)
        key1 = TemperatureTimeCourse.datetime_to_key(t1_aware)
        entry0 = self[key0]
        entry1 = self[key1]
        # iterate and integrate
        sum: float = 0.0
        it = self.irange(key0, key1)
        k0 = next(it)
        for k in it:
            temp0 = self.get(k0)
            temp1 = self.get(k)
            sum += ((temp1 + temp0) / 2) * (k - k0)
            k0 = k
        # calc mean and return
        return sum / (key1 - key0)
    
    def calc_day_mean_temperature(self, d: date, tz = None) -> int:
        if tz is None:
            tz = TemperatureTimeCourse.berlin
        t0 = datetime.combine(d, time(0,0), tz)
        d1 = d + timedelta(days=1)
        t1 = datetime.combine(d1, time(0,0), tz)
        temp = self.calc_mean_temperature(t0, t1)
        return temp
    
    def calc_temperature(self, t: datetime) -> float:
        t_aware = self.assure_awareness(t)
        temp = float(self[TemperatureTimeCourse.datetime_to_key(t_aware)]['TT_TU'])
        return temp
    