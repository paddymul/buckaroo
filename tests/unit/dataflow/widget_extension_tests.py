import pytest
from buckaroo.dataflow.widget_extension_utils import (
    find_most_specific_styling, analysis_extend, get_styling_analysis,
    InvalidArgumentException,
    configure_buckaroo)
from buckaroo.customizations.styling import (DefaultSummaryStatsStyling, DefaultMainStyling, obj_)
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
    #Custom_1 doesn't extend BaseStylingKlass, so it won't work
    assert [Custom_1] == analysis_extend(BuckarooWidget, analysis_klasses=[Custom_1])

    base_len = len(BuckarooWidget.analysis_klasses)
    extra_kls_lst = analysis_extend(BuckarooWidget, extra_analysis_klasses=[Custom_1])
    assert Custom_1 in extra_kls_lst
    assert len(extra_kls_lst) == (base_len) + 1

    with pytest.raises(InvalidArgumentException):
        analysis_extend(BuckarooWidget, extra_analysis_klasses=[Custom_1], analysis_klasses=[ExtendedCustomStyling])

def test_get_styling_analysis():

    foo_row = obj_('foo')

    base_pinned_row_len = len(DefaultMainStyling.pinned_rows)
    ExtraFooStyling = get_styling_analysis(
        DefaultMainStyling,
        extra_pinned_rows=[foo_row])

    assert foo_row in ExtraFooStyling.pinned_rows
    assert len(ExtraFooStyling.pinned_rows) == (base_pinned_row_len + 1)

    ReplacePinnedStyling = get_styling_analysis(DefaultMainStyling, pinned_rows=[foo_row])
    assert ReplacePinnedStyling.pinned_rows == [foo_row]
    with pytest.raises(InvalidArgumentException):
        get_styling_analysis(DefaultMainStyling, extra_pinned_rows=[1], pinned_rows=[2])
    
