from buckaroo.buckaroo_widget import BuckarooWidget
#from buckaroo.customizations.polars_analysis import
from .pluggable_analysis_framework.polars_analysis_management import (
    PlDfStats, BasicAnalysis)



class PolarsBuckarooWidget(BuckarooWidget):
    """TODO: Add docstring here
    """
    #command_classes = DefaultCommandKlsList
    analysis_classes = [BasicAnalysis]
    DFStatsClass = PlDfStats
