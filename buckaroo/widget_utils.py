import traceback
from .buckaroo_widget import BuckarooWidget
import pandas as pd
from datetime import datetime as dtdt
import os
import psutil


def is_in_ipython():

    try:
        from IPython.core.getipython import get_ipython
    except ImportError:
        raise ImportError('This feature requires IPython 1.0+')
    
    ip = get_ipython()
    if ip is None:
        #print("must be running inside ipython to enable default display via enable()")
        return False
    return ip
    

def enable(sampled=True,
           summaryStats=False,
           reorderdColumns=False,
           showCommands=False,
           auto_clean=False,
           postProcessingF=None,
           debug=False
           ):
    """
    Automatically use buckaroo to display all DataFrames
    instances in the notebook.

    """

    ip = is_in_ipython()

    parent_process = psutil.Process().parent()
    server_start_time = dtdt.fromtimestamp(parent_process.create_time())

    buckaroo_mtime = dtdt.fromtimestamp(os.path.getmtime(__file__))

    if buckaroo_mtime > server_start_time:
        print("""It looks like you installed Buckaroo after you started this notebook server. If you see a message like "Failed to load model class 'DCEFWidgetModel' from module 'buckaroo'", restart the jupyter server and try again.  If you have furter errors, please file a bug report at https://github.com/paddymul/buckaroo""")
        print("-"*80)
        print("buckaroo_mtime", buckaroo_mtime, "server_start_time", server_start_time)
        #note we don't throw an exception here because this is a
        #warning. I think this usecase specifically works on google
        #colab

    
    def _display_as_buckaroo(df):
        from IPython.display import display
        try:
            bw = BuckarooWidget(df,
                                debug=debug)
            return display(bw)
        except:
            if debug:
                traceback.print_exc()
                return
            # returning NotImplementedError causes IPython to find the
            # next registered formatter for the type
            raise NotImplementedError

    def _display_polars_as_buckaroo(polars_df):
        from IPython.display import display
        from buckaroo.polars_buckaroo import PolarsBuckarooWidget

        try:
            return display(PolarsBuckarooWidget(polars_df))
        except:
            if debug:
                traceback.print_exc()
                return
            raise NotImplementedError

    ip_formatter = ip.display_formatter.ipython_display_formatter
    ip_formatter.for_type(pd.DataFrame, _display_as_buckaroo)
    
    try:
        import polars as pl
        ip_formatter.for_type(pl.DataFrame, _display_polars_as_buckaroo)
    except ImportError:
        pass
    return True

def disable():
    """
    disable bucakroo as the default display method for DataFrames

    """

    ip = is_in_ipython()
    
    ip_formatter = ip.display_formatter.ipython_display_formatter
    ip_formatter.type_printers.pop(pd.DataFrame, None)
    
    try:
        import polars as pl
        ip_formatter.type_printers.pop(pl.DataFrame, None)    
    except ImportError:
        pass
    print("The default DataFrame displayers have been restored. To re-enable Buckaroo use `from buckaroo import enable; enable()`")
