from .lispy import s
from .configure_utils import configure_buckaroo
import pandas as pd
import numpy as np

class Command(object):
    pass

class to_bool(Command):
    #argument_names = ["df", "col"]
    command_default = [s('to_bool'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        ser = df[col]
        df[col] = pd.to_numeric(ser, errors='coerce').dropna().astype('boolean').reindex(ser.index)
        return df

    @staticmethod 
    def transform_to_py(df, col):
        return "    df['%s'] = pd.to_numeric(df['%s'], errors='coerce').dropna().astype('boolean').reindex(df['%s'].index)" % (col, col, col)

class to_datetime(Command):
    #argument_names = ["df", "col"]
    command_default = [s('to_datetime'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        ser = df[col]
        df[col] =  pd.to_datetime(ser, errors='coerce').reindex(ser.index)
        return df

    @staticmethod 
    def transform_to_py(df, col):
        return "    df['%s'] = pd.to_datetime(df['%s'], errors='coerce').reindex(df['%s'].index)" % (col, col, col)

class to_int(Command):
    #argument_names = ["df", "col"]
    command_default = [s('to_int'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        ser = df[col]
        try:
            df[col] = pd.to_numeric(ser, errors='coerce').dropna().astype('Int64').reindex(ser.index)
        except:
            #just let pandas figure it out, we recommended the wrong type
            df[col] = pd.to_numeric(ser, errors='coerce')

        return df

    @staticmethod 
    def transform_to_py(df, col):
        return "    #to_int %s" % col

class to_float(Command):
    #argument_names = ["df", "col"]
    command_default = [s('to_float'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        ser = df[col]
        df[col] = pd.to_numeric(ser, errors='coerce').dropna().astype('float').reindex(ser.index)
        return df

    @staticmethod 
    def transform_to_py(df, col):
        return "    #to_float %s" % col

class to_string(Command):
    #argument_names = ["df", "col"]
    command_default = [s('to_string'), s('df'), "col"]
    command_pattern = [None]

    @staticmethod 
    def transform(df, col):
        ser = df[col]
        df[col] = ser.fillna(value="").astype('string').replace("", None).reindex(ser.index)
        return df

    @staticmethod 
    def transform_to_py(df, col):
        return "    #to_string %s" % col

