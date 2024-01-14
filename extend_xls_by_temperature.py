from datetime import timedelta
import pandas as pd
import getdwddata

xls_fn : str = './Ablesung-Gas.xlsx'
xls_fn_out : str = './GasverbrauchKorrelationTemperatur.100.xlsx'
faktor_kwh_per_m3 = 9.82
warmwasser_energy_per_day = 0.75 * faktor_kwh_per_m3

df = pd.read_excel(xls_fn, sheet_name='Sheet1', engine='openpyxl', dtype='string')
df["Ablesezeitpunkt"]=pd.to_datetime(df["Ablesezeitpunkt"], format="%Y-%m-%d %H:%M:%S")
df["Zählerstand"]=pd.to_numeric(df["Zählerstand"])
n=len(df)
data = {'t0':[], 't1':[], 'dt':[], 'zählerstand0':[], 'zählerstand1':[], 'verbrauch':[], 'temperatur':[], 'energy_per_day':[]}
for i in range(1,len(df)):
    t0 = df.iloc[i-1]['Ablesezeitpunkt']
    t1 = df.iloc[i]['Ablesezeitpunkt']
    dt : timedelta = t1 -t0
    temperature = getdwddata.calc_mean_temperature(t0, t1)
    energieverbrauch_per_day = (df.iloc[i]['Zählerstand'] - df.iloc[i-1]['Zählerstand']) * faktor_kwh_per_m3 * 86400 / dt.total_seconds() - warmwasser_energy_per_day
    data['t0'].append(t0)
    data['t1'].append(t1)
    data['dt'].append(dt.total_seconds()/86400)
    data['zählerstand0'].append(df.iloc[i-1]['Zählerstand'])
    data['zählerstand1'].append(df.iloc[i]['Zählerstand'])
    data['verbrauch'].append(df.iloc[i]['Zählerstand'] - df.iloc[i-1]['Zählerstand'])
    data['temperatur'].append(temperature)
    data['energy_per_day'].append(energieverbrauch_per_day)
    print(f"von={t0}, bis={t1}, energieverbrauch/d={energieverbrauch_per_day:6.2f}, days={dt.total_seconds()/86400:5.2f}, temperature={temperature:5.2f}")
dfout = pd.DataFrame(data)
dfout.to_excel(xls_fn_out)
