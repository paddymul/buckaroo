from buckaroo.buckaroo_widget import BuckarooWidget
#from buckaroo.customizations.polars_analysis import
from .pluggable_analysis_framework.polars_analysis_management import (
    PlDfStats, BasicAnalysis)
#Do not merge this code to main, I don't want the project to require polars yet

class PolarsBuckarooWidget(BuckarooWidget):
    """TODO: Add docstring here
    """
    #command_classes = DefaultCommandKlsList
    analysis_classes = [BasicAnalysis]
    DFStatsClass = PlDfStats
