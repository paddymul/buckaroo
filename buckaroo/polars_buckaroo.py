from buckaroo.buckaroo_widget import BuckarooWidget
from .customizations.polars_analysis import PL_Analysis_Klasses
from .pluggable_analysis_framework.polars_analysis_management import (
    PlDfStats)
from .serialization_utils import pd_to_obj
from buckaroo.customizations.polars_commands import (
    DropCol, FillNA, GroupBy #, OneHot, GroupBy, reindex
)
from traitlets import Unicode
from ._frontend import module_name, module_version
from .customizations.styling import DefaultSummaryStatsStyling, DefaultMainStyling


local_analysis_klasses = PL_Analysis_Klasses.copy()
local_analysis_klasses.extend(
    [DefaultSummaryStatsStyling, DefaultMainStyling])

class PolarsBuckarooWidget(BuckarooWidget):
    """TODO: Add docstring here
    """
    command_classes = [DropCol, FillNA, GroupBy]
    analysis_klasses = local_analysis_klasses
    DFStatsClass = PlDfStats


    _model_name = Unicode('DCEFWidgetModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('DCEFWidgetView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    def _sd_to_jsondf(self, sd):
        """exists so this can be overriden for polars  """
        import pandas as pd
        temp_sd = sd.copy()

        #FIXME add actual test around weird index behavior
        # if 'index' in temp_sd:
        #     del temp_sd['index']
        return pd_to_obj(pd.DataFrame(temp_sd))

    def _df_to_obj(self, df):
        import pandas as pd
        #FIXME HACK
        if isinstance(df, pd.DataFrame):
            return pd_to_obj(df)

        else:
            return pd_to_obj(df.to_pandas())
