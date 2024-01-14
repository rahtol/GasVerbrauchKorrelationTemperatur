from datetime import date, time, datetime
import getdwddata


d = date(2024,1,1)
t0 = datetime.combine(d, time(0,0), getdwddata.tz_berlin)
t1 = datetime.combine(d, time(23,59), getdwddata.tz_berlin)

temp= getdwddata.calc_mean_temperature(t0, t1)
print(temp)
