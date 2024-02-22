from buckaroo.dataflow.widget_extension_utils import (
    find_most_specific_styling, analysis_extend, get_styling_analysis,
    configure_buckaroo)
from buckaroo.customizations.styling import (DefaultSummaryStatsStyling, DefaultMainStyling)
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)


def foo():
    print(find_most_specific_styling, analysis_extend, get_styling_analysis, configure_buckaroo)

def test_find_most_specific_styling():

    class Custom_1(ColAnalysis):
        pass

    class CustomStyling(DefaultMainStyling):
        pinned_rows= ['foo']

    class ExtendedCustomStyling(CustomStyling):
        pinned_rows= ['foo', 'bar']
        

    # Custom_1 doesn't extend DefaultMain, it looses
    assert find_most_specific_styling([Custom_1, DefaultMainStyling]) == DefaultMainStyling
    #order shouldn't matter
    assert find_most_specific_styling([DefaultMainStyling, Custom_1]) == DefaultMainStyling


    assert find_most_specific_styling([CustomStyling, DefaultMainStyling]) == CustomStyling
    assert find_most_specific_styling([DefaultMainStyling, CustomStyling]) == CustomStyling
    

    assert find_most_specific_styling([ExtendedCustomStyling, CustomStyling, DefaultMainStyling]) == ExtendedCustomStyling
    assert find_most_specific_styling([DefaultMainStyling, CustomStyling, ExtendedCustomStyling]) == ExtendedCustomStyling

def test_analysis_extend():
    pass
