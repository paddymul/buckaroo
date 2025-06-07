#def generate_column_config(df:pd.DataFrame, summary_dict) -> List[ColumnConfig]:
from turtle import pd
from typing import Any, Union
from buckaroo.serialization_utils import force_to_pandas, pd_to_obj

"these functions are generically useful for trying to serialize dataframes"



def generate_column_config(df:pd.DataFrame, summary_dict):
    ret_conf = []
    index_name = df.index.name or "index"
    ret_conf.append({'col_name':index_name, 'displayer_args' : { 'displayer':'obj'}})
    for col in df.columns:
        ret_conf.append({'col_name': str(col), 'displayer_args' : { 'displayer':'obj'} })
    return ret_conf
        

def df_to_obj(unknown_df:Union[pd.DataFrame, Any], summary_dict:Any):
    df = force_to_pandas(unknown_df)
    
    data = pd_to_obj(df)
    #dfviewer_config:DFViewerConfig = {
    dfviewer_config = {
        'pinned_rows'   : [],
        'column_config' : generate_column_config(df, summary_dict)
    }
    return {'data':data, 'dfviewer_config': dfviewer_config}


def test_df_to_obj():
    named_index_df = pd.DataFrame(
        dict(names=['one', 'two', 'three'],
             values=[1, 2, 3])).set_index('names')

    serialized_df = df_to_obj(named_index_df, {})
    assert serialized_df['data'][0]['names'] == 'one'
