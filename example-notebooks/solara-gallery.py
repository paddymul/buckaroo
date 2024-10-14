import json
import solara
import pandas as pd
from buckaroo.solara_buckaroo import SolaraDFViewer

obj_df = pd.DataFrame({
    'bools':[True, True, False, False, True, False],
    'ints': [   5,   20,    30,   -10, 7772, 5],
    #'timestamp':["2020-01-01 01:00Z", "2020-01-01 02:00Z", "2020-02-28 02:00Z", "2020-03-15 02:00Z", None, None],
    #'dicts': [ {'a':10, 'b':20, 'c':'some string'}, None, None, None, None, None], #polars
    #'nested_dicts': [{'level_1': {'a':10, 'b':20, 'c':'some string'}}, None, None, None, None, None],
    #'lists': [['a','b'], [1,2], None, None, None, None],
    #'lists-string': [['a','b'], ['foo', 'bar'], None, None, None, None],
    #'lists-int': [[10, 20], [100, 500], [8], None, None, None]
    }
)


base_str_col = ["asdf", "qwerty", "really long string, much  much longer",
             None,  "A"]

str_df = pd.DataFrame({
        'strings_string_displayer_max_len': base_str_col,
        'strings_obj_displayer':  base_str_col,
        'strings_string_displayer': base_str_col,
})
str_config =  {
        'strings_string_displayer_max_len': {'displayer_args': {'displayer': 'string', 'max_length':15}},
        'strings_obj_displayer':  {'displayer_args': {'displayer': 'obj'}},      
        'strings_string_displayer': {'displayer_args': {'displayer': 'string'}},
    }



def float_conf_col(min_digits, max_digits):
    return {'displayer_args': { 'displayer': 'float', 'min_fraction_digits':min_digits, 'max_fraction_digits': max_digits}}
float_config = {
        'float_obj_displayer':  {'displayer_args': {'displayer': 'obj'}},      
        'float_float_displayer_1__3' : float_conf_col(1,3),
        'float_float_displayer_0__3' : float_conf_col(0,3),
        'float_float_displayer_3__3' : float_conf_col(3,3),
        'float_float_displayer_3_13' : float_conf_col(3,13)}
float_col = [5, -8, 13.23, -8.01, -999.345245234, None]
float_df = pd.DataFrame({
    'float_obj_displayer': float_col,
    'float_float_displayer_1__3': float_col,
    'float_float_displayer_0__3': float_col,
    'float_float_displayer_3__3': float_col,
    'float_float_displayer_3_13': float_col})

configs = {"str_config" : (str_df, str_config),
           "float_config": (float_df, float_config)}
active_config = solara.reactive("str_config")



@solara.component
def Page():

    solara.Select(label="Config", 
    value=active_config, 
    values=list(configs.keys()))

    conf = configs[active_config.value]
    formatted_conf = json.dumps(conf[1], indent=4)

    json_code = f"""
```python
{formatted_conf}
```"""
    solara.Markdown(json_code)
    bw = SolaraDFViewer(df=conf[0],
        column_config_overrides = conf[1]
    )


