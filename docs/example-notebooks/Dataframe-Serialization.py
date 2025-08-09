import marimo

__generated_with = "0.12.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from io import StringIO, BytesIO
    import time
    from datetime import date


    from IPython.display import Javascript
    import pandas as pd
    import numpy as np

    import anywidget
    import traitlets

    #import buckaroo
    return (
        BytesIO,
        Javascript,
        StringIO,
        anywidget,
        date,
        np,
        pd,
        time,
        traitlets,
    )


@app.cell
def _(date, np, pd):
    bool_df = pd.DataFrame([{'a':False}, {'a':True}])
    numeric_columns = pd.DataFrame([['foo', 8], ['bar',23]])
    object_values = pd.DataFrame([
        {'a':{'foo':9, 'bar':10}},
        {'a':{'foo':3, 'bar':5}}])
    object_values_varied = pd.DataFrame([
        {'a':{'foo':9, 'qux':10}},
        {'a':{'foo':3, 'bar':5}}])
    odd_integer_values = pd.DataFrame([
        {'a':np.nan},
        {'a':np.inf * -1},
        {'a':np.inf},
        {'a':np.iinfo(np.int64).min},
        {'a':np.iinfo(np.int64).max},
    ])
    over_64 = pd.DataFrame([
        {'a':np.nan},
        {'a':np.iinfo(np.int64).min * 2},
        {'a':np.iinfo(np.int64).max * 2},
    ])
    lists_df = pd.DataFrame([
        {'a': [10, 20, 30]},
        {'a': [30, 20, 40]}])
    timestamps = pd.DataFrame([{'a':pd.Timestamp('now')},
                                {'a':pd.Timestamp('2014-01-02')}])
    date_values = pd.DataFrame([{'a': date(2008, 5,24)},
                                {'a': date(2024, 11,13)}])
    uneven_lists_df = pd.DataFrame([
        {'a': [10, 20, 30]},
        {'a': [30, 40]}])
    categorical_df = pd.DataFrame({'a': pd.Categorical(['a', 'b', 'c', 'a', 'b', 'c'])})
    multi_index_rows = pd.DataFrame(
        [{'a':10}, {'a':20}, {'a':30}, {'a':40}, {'a':50}],
        index=pd.MultiIndex.from_tuples(
            [('foo', 3), ('foo', 4), ('bar', 3), ('bar', 4), ('bar', 5)]))
    string_index = pd.DataFrame([{'a':10}, {'a':20}], index=["foo", "bar"])
    mixed_bool_str = pd.DataFrame([
        {'a': 'a string'},
        {'a': True},
        {'a': False}])


    return (
        bool_df,
        categorical_df,
        date_values,
        lists_df,
        mixed_bool_str,
        multi_index_rows,
        numeric_columns,
        object_values,
        object_values_varied,
        odd_integer_values,
        over_64,
        string_index,
        timestamps,
        uneven_lists_df,
    )


@app.cell
def _(BytesIO, anywidget, bool_df, mixed_bool_str, pd, traitlets):
    def bucakroo_to_parquet(df):
        obj_columns = df.select_dtypes([pd.CategoricalDtype(), 'object']).columns.to_list()
        encodings = {k:'json' for k in obj_columns}
        return df.to_parquet(engine='fastparquet', object_encoding=encodings)
        pd.read_parquet(BytesIO(mixed_bool_str.to_parquet(engine='fastparquet', object_encoding={'a':'bson'})), engine='fastparquet')
    class SerializationWidget(anywidget.AnyWidget):
        _esm = """
        import * as hyparquet from "https://cdn.jsdelivr.net/npm/hyparquet@1.8.4/+esm";
        function render({ model, el }) {
          console.log("hyparquet", hyparquet)

            const table_bytes = model.get("df_parquet")
            console.log("table_bytes", table_bytes.length, table_bytes)
            const metadata = hyparquet.parquetMetadata(table_bytes.buffer)
            console.log("metadata", metadata)
            hyparquet.parquetRead({
                file: table_bytes.buffer,
                metadata:metadata,
                rowFormat: 'object',
                onComplete: data => {
                    const parqData = data;
                    console.log("parqData", parqData)
                    model.set("df_json", data)
                    model.save_changes();
                }
          })
        }
        export default { render };
        """
        df_parquet = traitlets.Bytes().tag(sync=True)
        df_json = traitlets.Any().tag(sync=True)

    cw = SerializationWidget(df_parquet=bucakroo_to_parquet(bool_df))
    cw
    #check the javascript console to see what cw logged
    return SerializationWidget, bucakroo_to_parquet, cw


@app.cell
def _(
    Javascript,
    SerializationWidget,
    bool_df,
    bucakroo_to_parquet,
    display,
    pd,
    time,
):
    from jupyter_ui_poll import ui_events
    #adapted from  https://stackoverflow.com/questions/54629964/how-to-pause-jupyter-notebook-widgets-waiting-for-user-input

    def rountrip_widget_df(df):
        """ just returns the df """
        try:
            cw2 = SerializationWidget(df_parquet=bucakroo_to_parquet(df))
            display(Javascript("console.clear()"))
            display(cw2)
            with ui_events() as poll:
                while cw2.df_json is None:
                    #waiting for user input
                    time.sleep(.1)
                    poll(1) # poll queued UI events including button
                    pass
            return pd.DataFrame(cw2.df_json)
        except:
            return "error"
    rountrip_widget_df(bool_df)
    return rountrip_widget_df, ui_events


@app.cell
def _(BytesIO, StringIO, pd, rountrip_widget_df):
    def roundtrip_json(df):
        return df.equals(pd.read_json(StringIO(df.to_json())))
    def roundtrip_feather(df):
        byts = BytesIO()
        try:
            df.to_feather(byts)
            return df.equals(pd.read_feather(byts))
        except:
            return "error"
    def roundtrip_parquet(df):
        try:
            return df.equals(pd.read_parquet(BytesIO(df.to_parquet())))
        except:
            return "error"
    def roundtrip_fastparquet(df):
        try:
            return df.equals(pd.read_parquet(BytesIO(df.to_parquet(engine='fastparquet')), engine='fastparquet'))
        except:
            return "error"

    def roundtrip_fastparquet_json(df):
        try:
            out = BytesIO(df.to_parquet(engine='fastparquet', object_encoding={'a': 'json'}))
            return df.equals(pd.read_parquet(out, engine='fastparquet'))
        except:
            return "error"
    def rountrip_widget_test(df):
        try:
            return df.equals(rountrip_widget_df(df))
        except:
            return "error"
    def roundtrip_pickle(df):
        df.to_pickle('byts')
        return df.equals(pd.read_pickle('byts'))
    return (
        roundtrip_fastparquet,
        roundtrip_fastparquet_json,
        roundtrip_feather,
        roundtrip_json,
        roundtrip_parquet,
        roundtrip_pickle,
        rountrip_widget_test,
    )


@app.cell
def _(
    bool_df,
    categorical_df,
    date_values,
    lists_df,
    mixed_bool_str,
    multi_index_rows,
    numeric_columns,
    object_values,
    object_values_varied,
    odd_integer_values,
    pd,
    roundtrip_fastparquet,
    roundtrip_fastparquet_json,
    roundtrip_feather,
    roundtrip_json,
    roundtrip_parquet,
    roundtrip_pickle,
    rountrip_widget_test,
    uneven_lists_df,
):
    dfs = dict(
        numeric_columns = numeric_columns,
        bool_df=bool_df,
        object_values = object_values,
        object_values_varied = object_values_varied,
        date_values = date_values,
        odd_integer_values = odd_integer_values,
        lists_df = lists_df,
        uneven_lists_df = uneven_lists_df,
        multi_index_rows = multi_index_rows,
        #multi_index_columns = multi_index_columns,
        mixed_bool_str = mixed_bool_str,
        categorical_df = categorical_df)
    results = []
    for k, df in dfs.items():
        results.append({
            'name':k,
            'json':roundtrip_json(df), 'feather':roundtrip_feather(df),
            'fast_parquet_json':roundtrip_fastparquet_json(df),
            'widget': rountrip_widget_test(df),

            'parquet':roundtrip_parquet(df),
            'fast_parquet':roundtrip_fastparquet(df), 
            'pickle': roundtrip_pickle(df), 
                       })
    #results_df = pd.DataFrame(results, index=dfs.keys())
    results_df = pd.DataFrame(results) #Buckaroo doesn't work with string indexes
    results_df
    return df, dfs, k, results, results_df


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
