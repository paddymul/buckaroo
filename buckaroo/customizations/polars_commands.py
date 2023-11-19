import polars as pl
#import numpy as np

from ..jlisp.lispy import s
#from ..jlisp.configure_utils import configure_buckaroo
#from ..auto_clean.cleaning_commands import (to_bool, to_datetime, to_int, to_float, to_string)

class Command(object):
    pass
    
class FillNA(Command):
    #argument_names = ["df", "col", "fill_val"]
    command_default = [s('fillna'), s('df'), "col", 8]
    command_pattern = [[3, 'fillVal', 'type', 'integer']]

    @staticmethod 
    def transform(df, col, val):
        return df.with_columns(pl.col(col).fill_null(val))
        return df

    @staticmethod 
    def transform_to_py(df, col, val):
        return "    df = df.with_columns(pl.col('%s').fill_null(%r))" % (col, val)

class DropCol(Command):
    #argument_names = ["df", "col"]
    command_default = [s('dropcol'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        return df.drop(col)
        return df

    @staticmethod 
    def transform_to_py(df, col):
        return "    df.drop_in_place('%s')" % col


class GroupBy(Command):
    command_default = [s("groupby"), s('df'), 'col', {}]
    command_pattern = [[3, 'colMap', 'colEnum', ['null', 'sum', 'mean', 'median', 'count']]]
    @staticmethod 
    def transform(df, col, col_spec):
        agg_clauses = []
        for k, v in col_spec.items():
            if v == "sum":
                agg_clauses.append(pl.col(k).sum().alias("%s(sum)" % k))
            elif v == "mean":
                agg_clauses.append(pl.col(k).mean().alias("%s(mean)" % k))
            elif v == "median":
                agg_clauses.append(pl.col(k).median.alias("%s(median)" % k))
            elif v == "count":
                agg_clauses.append(pl.col(k).drop_nulls().count().alias("%s(count)" % k))

        q = (
            df
            .lazy()
            .group_by(by=col)
            .agg(*agg_clauses)
            .sort(col, descending=True)
        )
        return q.collect()



    @staticmethod 
    def transform_to_py(df, col, col_spec):
        agg_clauses = []
        for k, v in col_spec.items():
            if v == "sum":
                agg_clauses.append("    pl.col('%s').sum().alias('%s(sum)')"  % (k, k))
            elif v == "mean":
                agg_clauses.append("    pl.col('%s').mean().alias('%s(mean)')"  % (k, k))
            elif v == "median":
                agg_clauses.append("    pl.col('%s').median().alias('%s(median)')"  % (k, k))
            elif v == "count":
                agg_clauses.append("    pl.col('%s').drop_nulls().count().alias('%s(count)')"  % (k, k))
        full_agg_text = ",\n".join(agg_clauses)
        command_template = """
    q = (
         df
        .lazy()
        .group_by(by='%s')
        .agg(%s)
        .sort('%s', descending=True)
        )
    df = q.collect()
        """
        return command_template % (col, full_agg_text, col)

'''

    
class OneHot(Command):
    command_default = [s('onehot'), s('df'), "col"]
    command_pattern = [None]
    @staticmethod 
    def transform(df, col):
        one_hot = pd.get_dummies(df[col])
        df.drop(col, axis=1, inplace=True)
        #how to make this inplace?
        return df.join(one_hot) 

    @staticmethod 
    def transform_to_py(df, col):
        commands = [
            "    one_hot = pd.get_dummies(df['%s'])" % (col),
            "    df.drop('%s', axis=1, inplace=True)" % (col),
            "    df = df.join(one_hot)"]
        return "\n".join(commands)

group_df = pd.DataFrame({'a':[10,20,30,40,50,60],
                   'b':[1,2,3,4,5,6],
                   'c':['q', 'q', 'q', 'q', 'w', 'w']})

def safe_int(x):
    try:
        return int(x)
    except:
        return np.nan

class SafeInt(Command):
    command_default = [s('safeint'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        df[col] = df[col].apply(safe_int)
        #df[col] = 5
        return df

    @staticmethod 
    def transform_to_py(df, col):
        return "    df['%s'] = df['%s'].apply(safe_int)" % (col, col)



class ato_datetime(Command):
    #argument_names = ["df", "col"]
    command_default = [s('to_datetime'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        df[col] = pd.to_datetime(df[col])
        return df

    @staticmethod 
    def transform_to_py(df, col):
        return "    df['%s'] = pd.to_datetime(df['%s'])" % (col, col)    

class reindex(Command):
    command_default = [s('reindex'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        old_col = df[col]
        df.drop(col, axis=1, inplace=True)
        df.index = old_col.values
   p     return df

    @staticmethod 
    def transform_to_py(df, col):
        return "\n".join(
            ["    old_col = df['%s']" % col,
             "    df.drop('%s', axis=1, inplace=True)" % col,
             "    df.index = old_col.values"])

DefaultCommandKlsList = [DropCol, SafeInt, FillNA, reindex, OneHot, GroupBy,
                         to_bool, to_datetime, to_int, to_float, to_string]
command_defaults, command_patterns, buckaroo_transform, buckaroo_to_py_core = configure_buckaroo(DefaultCommandKlsList)

'''
