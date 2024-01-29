from buckaroo.buckaroo_widget import BuckarooWidget
from .customizations.polars_analysis import PL_Analysis_Klasses
from .pluggable_analysis_framework.polars_analysis_management import (
    PlDfStats)
from .serialization_utils import pd_to_obj
from buckaroo.customizations.polars_commands import (
    DropCol, FillNA, GroupBy #, OneHot, GroupBy, reindex
)


class PolarsBuckarooWidget(BuckarooWidget):
    """TODO: Add docstring here
    """
    command_classes = [DropCol, FillNA, GroupBy]
    analysis_klasses = PL_Analysis_Klasses
    DFStatsClass = PlDfStats



    def _sd_to_jsondf(self, sd):
        """exists so this can be overriden for polars  """
        import pandas as pd
        temp_sd = sd.copy()
        #FIXME add actual test around weird index behavior
        if 'index' in temp_sd:
            del temp_sd['index']
        return pd_to_obj(pd.DataFrame(temp_sd))

    def _df_to_obj(self, df):
        return pd_to_obj(df.to_pandas())


