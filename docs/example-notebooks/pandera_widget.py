import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import pandera.pandas as pa
    from pandera import Column, Check
    from buckaroo.buckaroo_widget import BuckarooInfiniteWidget
    return Check, Column, pa, pd


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


app._unparsable_cell(
    r"""
    available_fruits = [\"apple\", \"banana\", \"orange\"]
    nearby_stores = [\"Aldi\", \"Walmart\"]

    schema = pa.DataFrameSchema(    {
            \"name\": Column(str, Check.isin(available_fruits)),
            \"store\": Column(str, Check.isin(nearby_stores)),
            \"price\": Column(int, Check.less_than(4)),
        }
    )
    #val_result = schema.validate(fruits)
    schema.
    """,
    name="_"
)


@app.cell
def _(Check, Column, pa, pd):
    schema2 = pa.DataFrameSchema(
        {
            "customer_id": Column(
                dtype="int64",  # Use int64 for consistency
                checks=[
                    Check.isin(range(1, 1000)),  # IDs between 1 and 999
                    Check(lambda x: x > 0, element_wise=True)], # IDs must be positive
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
                    Check.less_than_or_equal_to(120)],  # Age must be reasonable
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
            "customer_id": [None, 2000, 3, 4, "invalid"],  # "invalid" is not an integer
           #"customer_id": [1, 2, 3, 4, -5],  # "invalid" is not an integer
            "name": ["Maryam", "Jane", "", "Alice", "Bobby"],  # Empty name
            "age": [25, -5, 30, 45, 35],  # Negative age is invalid
            "email": [
                "mrym@gmail.com",
                "jane.s@yahoo.com",
                "invalid_email",
                "alice@google.com",
                #None,
                'asdfasf'
            ]})
    return kd_df, schema2


@app.cell
def _(kd_df):
    kd_df
    return


@app.cell
def _(get_fails, kd_df):
    error_df = get_fails(kd_df)
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


app._unparsable_cell(
    r"""
     from collections import defaultdict

    orig_column_errortype_count = defaultdict(lambda : 0)
    tuple_col_num = {}
    for col, err_type in cross_df1.columns:
        orig_column_errortype_count[col] += 1
        tuple_col_num[(col, err_type)] = orig_column_errortype_count[col] 
    #orig_column_errortype_count
    tuple_col_num
    for k in cross_df1.columns:
        cross_df1[k] = cross_df1[k].replace(1, tuple_col_num[k])
    #cross_df1
    _error_num_data = {}
    for first_level in cross_df1.columns.get_level_values(0).unique():
        _error_num_data[first_level+\"_color\"] = cross_df1.xs(first_level, axis=1, level=0).sum(axis=1)
    pd.DataFrame(_error_num_data)  # this will be used to uniquely highlight error states
    """,
    name="_"
)


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
def _(pd):
    unjoined_df = pd.DataFrame({'a': pd.Series(['foo', pd.NA, 'baz', pd.NA], dtype=pd.StringDtype), 
                                'b':pd.Series([pd.NA, '2', '3', pd.NA], dtype=pd.StringDtype)})
    unjoined_df.fillna('').agg('\\n'.join, axis=1).astype('string').replace('',pd.NA)
    return


@app.cell
def _():
    return


@app.cell
def _(cross_df1):
    cross_df1.xs('name', axis=1, level=0)
    return


@app.cell
def _(cross_df1):
    cross_df1['customer_id']
    return


@app.cell
def _(cross_df1):
    cross_df1['customer_id'].sum(axis=1)
    return


@app.cell
def _(cross_df1, pd):
    #cross_df1['customer_id'].astype('boolean').replace(False, pd.NA)
    cross_df1.astype('Int64').replace(0, pd.NA)
    return


@app.cell
def _(pd):
    def prepare_error_df_columns(error_df):
        cross_df = pd.crosstab(error_df['error_index'], [error_df['column'], error_df['check']])



    return


@app.cell
def _(kd_df, pa, schema2):
    def get_fails(df):
        try:
            validated_df = schema2.validate(kd_df, lazy=True)
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
def _(input_df, pd):
    def transform_to_boolean_matrix(input_df):
        # Create a cross-tabulation of column and reason for each fake_index
        pivot = pd.crosstab(
            input_df['fake_index'],
            [input_df['column'], input_df['reason']],
            dropna=False
        )

        # Flatten the multi-level columns
        pivot.columns = [f"{col[0]}_reason_{col[1]}" for col in pivot.columns]

        # Convert to boolean with NA values
        result = pivot.astype(pd.BooleanDtype())

        return result
    transform_to_boolean_matrix(input_df).replace(False, pd.NA)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
