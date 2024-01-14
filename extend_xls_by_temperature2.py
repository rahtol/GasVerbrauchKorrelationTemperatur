from datetime import datetime, timedelta
import pandas as pd
from TemperatureTimeCourse import TemperatureTimeCourse

xls_fn : str = './Ablesung-Gas.xlsx'
xls_fn_out : str = './GasverbrauchKorrelationTemperatur.100.xlsx'
faktor_kwh_per_m3 = 9.82
warmwasser_energy_per_day = 0.60 * faktor_kwh_per_m3
station13777 = TemperatureTimeCourse()

df = pd.read_excel(xls_fn, sheet_name='Sheet1', engine='openpyxl', dtype='string')

data = {'t0':[], 't1':[], 'dt':[], 'zählerstand0':[], 'zählerstand1':[], 'verbrauch':[], 'temperatur':[], 'energy_per_day':[]}
for i in range(1,len(df)):
    if pd.notna(df.iloc[i]['Bemerkung']):
        print(f'i={i}, Bemerkung={df.iloc[i]["Bemerkung"]}')
    else:
        t0 = datetime.strptime(df.iloc[i-1]["Ablesezeitpunkt"], "%Y-%m-%d %H:%M:%S")
        t1 = datetime.strptime(df.iloc[i]["Ablesezeitpunkt"], "%Y-%m-%d %H:%M:%S")
        z0 = float(df.iloc[i-1]["Zählerstand"])
        z1 = float(df.iloc[i]["Zählerstand"])
        dt : timedelta = t1-t0
        temperature = station13777.calc_mean_temperature(t0, t1)
        energieverbrauch_per_day = (z1-z0) * faktor_kwh_per_m3 * 86400 / dt.total_seconds() - warmwasser_energy_per_day
        data['t0'].append(t0)
        data['t1'].append(t1)
        data['dt'].append(dt.total_seconds()/86400)
        data['zählerstand0'].append(z0)
        data['zählerstand1'].append(z1)
        data['verbrauch'].append(z1-z0)
        data['temperatur'].append(temperature)
        data['energy_per_day'].append(energieverbrauch_per_day)
        print(f"i={i}, von={t0}, bis={t1}, energieverbrauch kWh/d={energieverbrauch_per_day:6.2f}, days={dt.total_seconds()/86400:5.2f}, temperature={temperature:5.2f}")

dfout = pd.DataFrame(data)
dfout.to_excel(xls_fn_out)
