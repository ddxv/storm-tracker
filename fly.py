from tropycal import realtime

realtime_obj = realtime.Realtime()

active_storms = realtime_obj.list_active_storms(basin="east_pacific")

storm = realtime_obj.get_storm()

realtime_obj.plot_summary(domain="east_pacific")

p = realtime_obj.plot_summary(domain={"w": -100, "e": -10, "s": 4, "n": 60})

p.show()
