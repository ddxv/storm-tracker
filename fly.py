from tropycal import realtime

realtime_obj = realtime.Realtime()

realtime_obj.list_active_storms(basin='east_pacific')

realtime_obj.plot_summary(domain='east_pacific')



