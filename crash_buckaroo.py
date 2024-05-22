import pandas as pd
import numpy as np
import buckaroo
#import fastf1
#ev2020 = fastf1.get_event_schedule(2020)
#small_df = ev2020[ev2020.columns[4:5]][:1]
#print(small_df)
#print("="*80)
#print(small_df.dtypes)
#print(small_df.to_json())
df = pd.read_json("""{"EventDate":{"0":1582243200000}}""")
ab = df['EventDate'].apply(pd.to_datetime)
df2= pd.DataFrame({'EventDate': ab.astype('object')})
#buckaroo.BuckarooWidget(df2) #crashes
from buckaroo.pluggable_analysis_framework.analysis_management import DfStats
from buckaroo.customizations.analysis import (TypingStats, ComputedDefaultSummaryStats, DefaultSummaryStats)
from buckaroo.customizations.histogram import (Histogram)
from buckaroo.customizations.styling import (DefaultSummaryStatsStyling, DefaultMainStyling)
from buckaroo.dataflow.dataflow import CustomizableDataflow, StylingAnalysis, exception_protect

analysis_klasses = [#TypingStats,
                        #Histogram,
#                        ComputedDefaultSummaryStats,
                        #                        StylingAnalysis,
                        DefaultSummaryStats,
                        #DefaultSummaryStatsStyling, DefaultMainStyling
                    ]
dfs = DfStats(df2, analysis_klasses)
#print(dfs.sdf)
bad_df = pd.DataFrame(dfs.sdf)
#bad_df.to_pickle('foo.pckl')


reified_df = pd.read_pickle('foo.pckl')
print(reified_df)
reified_df[['index', 'EventDate']].loc[['value_counts', 'nan_count']].to_json(orient='table')

#

reified_df.to_pickle('simplified_df.pckl')

simplified_df = pd.read_pickle('simplified_df.pckl')
#pd.show_versions()
print("before to_json")
simplified_df.to_json(orient='table')
print("after  to_json")
1/0

# print(reified_df)
# print(reified_df.dtypes)
# print(reified_df.to_json())

# print('='*80)
# val = reified_df['EventDate'][0]
# print(val)
# print(val.dtypes)
# print("type", type(val))
# print(val.to_json())
# print('-'*80)
# reified_df = pd.DataFrame({'EventDate': [pd.Series({'value_counts': {pd.Timestamp(1582243):1}})]}, index=['value_counts'])
# print(reified_df.to_json())
# reified_df.to_json(orient='table')
# print("after reified_df")

# timestamp_df = pd.DataFrame({'ab': [pd.Timestamp(1582243)]})

# vc_vals = pd.DataFrame({'ab_stats' : {'length':1, 'min': np.nan, 'max': np.nan, 'mean': 0, 'vc': timestamp_df['ab'].value_counts()}})
# print("vc_vals", vc_vals)
# vc_vals.to_json(orient='table')
# print("vc_vals finsihed")
# serialized = pd.DataFrame(dfs.sdf).to_json(orient='table') #, indent=2, default_handler=str)

# #buckaroo.BuckarooWidget(df2)

# print("finished")
