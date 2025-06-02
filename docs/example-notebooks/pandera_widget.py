import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import pandera.pandas as pa
    from pandera import Column, Check
    from buckaroo.buckaroo_widget import BuckarooInfiniteWidget
    from collections import defaultdict
    return BuckarooInfiniteWidget, Check, Column, defaultdict, pa, pd


@app.cell
def _(pd):
    fruits = pd.DataFrame(
        {
            "name": ["apple", "banana", "apple", "orange"],
            "store": ["Aldi", "Walmart", "Walmart", "Aldi"],
            "price": [2, 1, 3, 4],
        }
    )

    fruits
    return


@app.cell
def _(Check, Column, pa):
    available_fruits = ["apple", "banana", "orange"]
    nearby_stores = ["Aldi", "Walmart"]

    schema = pa.DataFrameSchema(    {
            "name": Column(str, Check.isin(available_fruits)),
            "store": Column(str, Check.isin(nearby_stores)),
            "price": Column(int, Check.less_than(4)),
        }
    )
    #val_result = schema.validate(fruits)
    #schema.
    return


@app.cell
def _(Check, Column, pa, pd):
    def is_odd(val):
        return val %2 == 1
    schema2 = pa.DataFrameSchema(
        {
            "customer_id": Column(
                dtype="int64",  # Use int64 for consistency
                checks=[
                    Check(lambda x: x > 0, element_wise=True), # IDs must be positive
                    Check(is_odd, element_wise=True),
                    Check.isin(range(-50, 1000)), 
                    Check.isin(range(0, 1000))
                ],  # IDs between 1 and 999
                nullable=False),
            "name": Column(
                dtype="string",
                checks=[
                    Check.str_length(min_value=1),  # Names cannot be empty
                    Check(lambda x: x.strip() != "", element_wise=True)],
                nullable=False),
            "age": Column(
                dtype="int64",
                checks=[
                    Check.greater_than(0),  # Age must be positive
                    Check.less_than_or_equal_to(120),
                ],  # Age must be reasonable
                nullable=False),
            "email": Column(
                dtype="string",
                checks=[
                    Check.str_matches(
                        r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")],
                nullable=False,
            )})
    kd_df = pd.DataFrame(
        {
            #"customer_id": [None, -20, 3, 4, "invalid", 2000],  # "invalid" is not an integer
            "customer_id": pd.Series([pd.NA, -20, 3, 4, -5, 2000, 2001, 9], dtype='Int64'),  # "invalid" is not an integer
            "name": ["Maryam", "Jane", "", "Alice", "Bobby", "k", "v", "normal"],  # Empty name
            "age": [25, -5, 30, 45, 35, 150, 7, 25],  # Negative age is invalid
            "email": [
                "mrym@gmail.com",
                "jane.s@yahoo.com",
                "invalid_email",
                "alice@google.com",
                None,
                "asdasdf",
                None,
                'good@email.com'
            ]})
    return kd_df, schema2


@app.cell
def _(kd_df):
    kd_df
    return


@app.cell
def _(get_fails, kd_df, schema2):
    error_df = get_fails(kd_df, schema2)
    error_df
    return (error_df,)


@app.cell
def _(error_df, pd):
    cross_df1 = pd.crosstab(error_df['error_index'], [error_df['column'], error_df['check']])
    cross_df1 = cross_df1.astype('Int64').replace(0, pd.NA).dropna(axis=1, how='all')
    #cross_df1.columns = cross_df1.columns.get_level_values(1)
    cross_df1
    return (cross_df1,)


@app.cell
def _(calculate_error_color_num, cross_df1):
    calculate_error_color_num(cross_df1)
    return


@app.cell
def _(defaultdict, pd):
    def calculate_error_color_num(error_cross_df):

        orig_column_errortype_count = defaultdict(lambda : 0)
        tuple_col_num = {}
        for col, err_type in error_cross_df.columns:
            orig_column_errortype_count[col] += 1
            tuple_col_num[(col, err_type)] = orig_column_errortype_count[col] 

        new_data = {}
        for k in error_cross_df.columns:
            new_data[k] = error_cross_df[k].replace(1, tuple_col_num[k])

        unique_num_df = pd.DataFrame(new_data, columns=error_cross_df.columns)
        _error_num_data = {}

        for first_level in unique_num_df.columns.get_level_values(0).unique():
            _error_num_data[first_level+"_color"] = unique_num_df.xs(first_level, axis=1, level=0).sum(axis=1)
        return pd.DataFrame(_error_num_data)  # this will be used to uniquely highlight error states
    return (calculate_error_color_num,)


@app.cell
def _(cross_df1, pd):
    def get_column_reason_series(col_errors_df):
        """
        This function is about as far as possible from a vectorized operation.

        I couldn't figure it out.  Converting NA to '', means everything gets joined then you have to pull them out
        This would probably be cleaner as a tuple of non NA elements and a special displayer to make those work

        Open to suggestions
        """

        str_cust_error_data = {}
        for col in col_errors_df:
            base_ser = pd.Series([pd.NA] * len(col_errors_df), dtype='string', index=col_errors_df.index)
            base_ser.loc[col_errors_df[col]==1] = col
            str_cust_error_data[col] = base_ser
        str_err_df = pd.DataFrame(str_cust_error_data)

        ret_ser = []
        for idx, row in str_err_df.iterrows():
            dna = row.dropna()
            if len(dna) > 0:
                ret_ser.append('|'.join(dna.tolist()))
            else:
                ret_ser.append(dna.values[0])
        return pd.Series(ret_ser, index=str_err_df.index, dtype='string')
    get_column_reason_series(cross_df1.xs('customer_id', axis=1, level=0).dropna(how='all', axis=0))
    return (get_column_reason_series,)


@app.cell
def _(cross_df1, get_column_reason_series):
    get_column_reason_series(cross_df1.xs('age', axis=1, level=0).dropna(how='all', axis=0))
    return


@app.cell
def _(cross_df1, get_column_reason_series, pd):
    def get_reason_df(cross_errors_df):
        reason_data = {}
        for first_level in cross_errors_df.columns.get_level_values(0).unique():
            col_df = cross_errors_df.xs(first_level, axis=1, level=0).dropna(how='all', axis=0)
            reason_data[first_level+"_reason"] = get_column_reason_series(col_df)
        return pd.DataFrame(reason_data)    
    get_reason_df(cross_df1)
    return (get_reason_df,)


@app.cell
def _(calculate_error_color_num, cross_df1, get_reason_df):
    color_df = calculate_error_color_num(cross_df1)
    reason_df = get_reason_df(cross_df1)
    return color_df, reason_df


@app.cell
def _(color_df, kd_df, reason_df):
    kd_df.join(color_df, how='outer').join(reason_df, how='outer')
    return


@app.cell
def _(
    BuckarooInfiniteWidget,
    calculate_error_color_num,
    get_fails,
    get_reason_df,
    make_col_config_overrides,
    pd,
):
    def BuckarooPandera(df, schema):
        error_df = get_fails(df, schema)
        cross_df1 = pd.crosstab(error_df['error_index'], [error_df['column'], error_df['check']])
        cross_df1 = cross_df1.astype('Int64').replace(0, pd.NA).dropna(axis=1, how='all')
        color_df = calculate_error_color_num(cross_df1)
        reason_df = get_reason_df(cross_df1)
        complete_df = df.join(color_df, how='outer').join(reason_df, how='outer')
        cco = make_col_config_overrides(df)
        bw = BuckarooInfiniteWidget(
            complete_df, column_config_overrides=cco)
        return bw

    return (BuckarooPandera,)


@app.cell
def _(BuckarooPandera, kd_df, schema2):
    BuckarooPandera(kd_df, schema2)
    return


@app.cell
def _():
    eq_map = ["transparent", "pink", "#73ae80", "#90b2b3", "#6c83b5"];
    def make_col_config_overrides(df):
        column_config_overrides = {}
        for column in df:
            column_config_overrides[column] = {
                'tooltip_config': { 'tooltip_type':'simple', 'val_column': column+'_reason'},
                'color_map_config': {
                    'color_rule': 'color_categorical',
                    'map_name': eq_map,
                    'val_column': column + "_color"}}
        return column_config_overrides
    return (make_col_config_overrides,)


app._unparsable_cell(
    r"""
    def make_col_config_overrides2(df):
            column_config_overrides['membership'] = {'merge_rule': 'hidden'}
        both_columns = [c for c in m_df.columns if df2_suffix in c] #columns that occur in both
        for b_col in both_columns:
            a_col = b_col.removesuffix(df2_suffix)
            col_neq = (m_df[a_col] == m_df[b_col]).astype('Int8') * 4 

            eq_col = a_col + \"|eq\"
            #by adding 2 and 4 to the boolean columns we get unique values
            #for combinations of is_null and value equal
            # this is then colored on the column
        
            m_df[eq_col] = col_neq + m_df['membership']

            column_config_overrides[b_col] = {'merge_rule': 'hidden'}
            column_config_overrides[eq_col] = {'merge_rule': 'hidden'}
            column_config_overrides[a_col] = {
                'tooltip_config': { 'tooltip_type':'simple', 'val_column': b_col},
                'color_map_config': {
                    'color_rule': 'color_categorical',
                    'map_name': eq_map,
                    'val_column': eq_col }}
        
        #where did the row come from 
        column_config_overrides[join_columns] =  {'color_map_config': {
              'color_rule': 'color_categorical',
              'map_name': eq_map,
              'val_column': 'membership'
            }}

    """,
    name="_"
)


@app.cell
def _(kd_df, pa):
    def get_fails(df, schema):
        try:
            validated_df = schema.validate(kd_df, lazy=True)
            print("Data is valid!")
            print(validated_df)
            return None
        except pa.errors.SchemaErrors as e:
            print("Validation failed with these problems:")
            #print(e.failure_cases[['column', 'check', 'failure_case', 'index']])
            err_df = e.failure_cases
            err_df['error_index'] = err_df['index']
            return err_df
    return (get_fails,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
