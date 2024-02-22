import pytest
from buckaroo.dataflow.widget_extension_utils import (
    find_most_specific_styling, analysis_extend, get_styling_analysis,
    InvalidArgumentException,
    configure_buckaroo)
from buckaroo.customizations.styling import (DefaultSummaryStatsStyling, DefaultMainStyling)
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)
from buckaroo.buckaroo_widget import BuckarooWidget

def foo():
    print(analysis_extend, get_styling_analysis, configure_buckaroo)

class Custom_1(ColAnalysis):
    pass

class CustomStyling(DefaultMainStyling):
    pinned_rows= ['foo']

class ExtendedCustomStyling(CustomStyling):
    pinned_rows= ['foo', 'bar']

def test_find_most_specific_styling():

        

    # Custom_1 doesn't extend DefaultMain, it looses
    assert find_most_specific_styling([Custom_1, DefaultMainStyling]) == DefaultMainStyling
    #order shouldn't matter
    assert find_most_specific_styling([DefaultMainStyling, Custom_1]) == DefaultMainStyling


    assert find_most_specific_styling([CustomStyling, DefaultMainStyling]) == CustomStyling
    assert find_most_specific_styling([DefaultMainStyling, CustomStyling]) == CustomStyling
    

    assert find_most_specific_styling([ExtendedCustomStyling, CustomStyling, DefaultMainStyling]) == ExtendedCustomStyling
    assert find_most_specific_styling([DefaultMainStyling, CustomStyling, ExtendedCustomStyling]) == ExtendedCustomStyling



def test_analysis_extend():

    assert [Custom_1] == analysis_extend(BuckarooWidget, analysis_klasses=[Custom_1])

    base_len = len(BuckarooWidget.analysis_klasses)

    extra_kls_lst = analysis_extend(BuckarooWidget, extra_analysis_klasses=[Custom_1])
    assert Custom_1 in extra_kls_lst
    assert len(extra_kls_lst) == (base_len) + 1

    with pytest.raises(InvalidArgumentException):
        analysis_extend(BuckarooWidget, extra_analysis_klasses=[Custom_1], analysis_klasses=[ExtendedCustomStyling])


