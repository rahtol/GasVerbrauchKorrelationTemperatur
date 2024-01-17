from TemperatureTimeCourse import TemperatureTimeCourse
from datetime import date, time, datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from AnnotatedCursor2 import AnnotatedCursor2

station13777 = TemperatureTimeCourse()

xls_fn :str = './Ablesung-Gas.xlsx'
df = pd.read_excel(xls_fn, sheet_name='Sheet1', engine='openpyxl', dtype='string')

faktor_kwh_per_m3 = 9.82
warmwasser_energy_per_day = 0.60 * faktor_kwh_per_m3
data = {'t0':[], 't1':[], 'dt':[], 'zählerstand0':[], 'zählerstand1':[], 'verbrauch':[], 'temperatur':[], 'energy_per_day':[]}
for i in range(1,len(df)):
    if pd.notna(df.iloc[i]['Bemerkung']):
        print(f'Skip: i={i}, Bemerkung={df.iloc[i]["Bemerkung"]}')
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
dfout = pd.DataFrame(data)

st = dfout['temperatur'].sum()
sy = dfout['energy_per_day'].sum()
stt = (dfout['temperatur']*dfout['temperatur']).sum()
sty = (dfout['temperatur']*dfout['energy_per_day']).sum()
n = len(dfout)

[a,b]=np.linalg.solve([[stt,st],[st,n]], [sty, sy])

t = dfout['temperatur']
y = dfout['energy_per_day']
y_mean = y.mean()
ssr = ((y - (a*t+b))**2).sum()
sst = ((y - y_mean)**2).sum()
R2 = 1 - (ssr/sst)

linear_regression = { 'a': a, 'b': b, 'R**2': R2}

x = np.linspace(dfout['temperatur'].min(),dfout['temperatur'].max(), num=2)
fig, ax = plt.subplots(figsize=(15,8))
ax.scatter('temperatur','energy_per_day', s=8*dfout['dt'], c='maroon', data=dfout)
ax.plot(x, a*x+b, linewidth=2)
ax.set_xlabel('Temperatur [°C]')
ax.set_ylabel('Gasverbrauch [kWh / day]')
ax.grid(True)
ax.text(16, 56, f'a={a:.3f}\nb ={b:6.3f}\n$R^2$={R2:.4f}', verticalalignment='top',bbox={'facecolor': 'linen', 'alpha': 0.8, 'pad': 10})
plt.title(f'Gasverbrauch korreliert zu Aussentemperatur\nZeitraum: {dfout.iloc[0]["t0"]} bis {dfout.iloc[-1]["t1"]}')
cursor = AnnotatedCursor2(
    data=dfout, 
    textprops={'color': 'black', 'fontweight': 'normal', 'fontsize': 'x-small', 
               'horizontalalignment': 'right', 'verticalalignment': 'top',
               'bbox': {'facecolor': 'linen', 'alpha': 0.8, 'pad': 2}}, 
    ax=ax, useblit=True, color='gray', linewidth=1, offset=(-8,-8), linear_regression=linear_regression)

plt.show()
