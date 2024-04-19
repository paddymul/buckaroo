import pandas as pd


simplified_df = pd.read_pickle('simplified_df.pckl')
pd.show_versions()
print("simplified_df")
print(simplified_df)
print("-" * 80)
print("simplified_df.dtypes")
print(simplified_df.dtypes)
print("-" * 80)
vc_bad_row = simplified_df['EventDate'].loc['value_counts']
print("vc_bad_row")
print(vc_bad_row)
print("-" * 80)
print("type(vc_bad_row)")
print(type(vc_bad_row))
print("-" * 80)
print("vc_bad_row.dtype")
print(vc_bad_row.dtype)
print("-" * 80)
print("before to_json")
simplified_df.to_json(orient='table')
print("after  to_json")
1/0
