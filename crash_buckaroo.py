import pandas as pd
import buckaroo
import fastf1
ev2020 = fastf1.get_event_schedule(2020)
small_df = ev2020[ev2020.columns[4:5]][:1]
print(small_df)

buckaroo.BuckarooWidget(small_df)

print("finished")
