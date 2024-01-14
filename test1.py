from datetime import date, time, datetime
from zoneinfo import ZoneInfo
from TemperatureTimeCourse import TemperatureTimeCourse

station13777 = TemperatureTimeCourse()
temp12 = station13777[TemperatureTimeCourse.measuring_time_to_key('2024010512', ZoneInfo('Europe/Berlin'))]['TT_TU']
temp13 = station13777[TemperatureTimeCourse.measuring_time_to_key('2024010513', ZoneInfo('Europe/Berlin'))]['TT_TU']
t: datetime = datetime.strptime('2024/01/05 12:30', '%Y/%m/%d %H:%M').astimezone(ZoneInfo('Europe/Berlin'))
#temp1230 = station13777[TemperatureTimeCourse.datetime_to_key(t)]['TT_TU']
temp1230 = station13777.calc_temperature(t)
print(f'tempt12={temp12}, temp13={temp13}, temp1230={temp1230}')

t0 = datetime.strptime('2023/03/26 00:00', '%Y/%m/%d %H:%M').astimezone(ZoneInfo('Europe/Berlin'))
t1 = datetime.strptime('2023/03/27 00:00', '%Y/%m/%d %H:%M').astimezone(ZoneInfo('Europe/Berlin'))

temp= station13777.calc_mean_temperature(t0, t1)
print(f'26.03.2023 temp={temp}')

d = date(2024,1,1)
t0 = datetime.combine(d, time(0,0), ZoneInfo('Europe/Berlin'))
#t1 = datetime.combine(d, time(23,59), ZoneInfo('Europe/Berlin'))
t1 = datetime.strptime('2024/01/02 00:00', '%Y/%m/%d %H:%M').astimezone(ZoneInfo('Europe/Berlin'))
temp= station13777.calc_mean_temperature(t0, t1)
print(f'01.01.2024 temp={temp:.2f}°C')

temp= station13777.calc_day_mean_temperature(date(2024,1,6))
print(f'06.01.2024 temp={temp:.2f}°C')

temp= station13777.calc_mean_temperature(datetime(2023,1,1), datetime(2024,1,1))
print(f'2023 temp={temp:.1f}°C')

for i in range(12):
    t0 = datetime(2023,i+1,1)
    t1 = datetime(2024 if i==11 else 2023, 1 if i==11 else i+2, 1)
    temp = station13777.calc_mean_temperature(t0, t1)
    print(f'{t0.strftime("%y/%m/%d")} - {t1.strftime("%y/%m/%d")}: {temp:.1f}°C')
