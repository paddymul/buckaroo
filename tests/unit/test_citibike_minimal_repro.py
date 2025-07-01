# state:READONLY
"""
Minimal reproduction of the citibike_df failure.

This test reproduces the specific polars error:
ERROR executing clause .rename_alias(selector.mode()): Series: ["tripduration", "most_freq"], 
length 1 doesn't match the DataFrame height of 10

FINDINGS: The error only occurs when ALL 5 core analysis classes are used together:
- VCAnalysis, BasicAnalysis, PlTyping, ComputedDefaultSummaryStats, HistogramAnalysis
"""

import polars as pl
from buckaroo.polars_buckaroo import PolarsBuckarooInfiniteWidget
from buckaroo.customizations.polars_analysis import (
    VCAnalysis, BasicAnalysis, PlTyping, ComputedDefaultSummaryStats, HistogramAnalysis
)
from buckaroo.customizations.styling import DefaultSummaryStatsStyling, DefaultMainStyling


# Create test data that reproduces the issue
def get_test_data():
    return pl.DataFrame({
        'tripduration': [558, 501, 116, 1151, 819, 330, 720, 480, 900, 650],
        'start_station_name': [
            'W 22 St & 8 Ave', 'E 25 St & 1 Ave', 'Canal St & Rutgers St',
            'LaGuardia Pl & W 3 St', 'E 9 St & Avenue C', 'Allen St & Hester St',
            'W 22 St & 8 Ave', 'E 25 St & 1 Ave', 'Canal St & Rutgers St',
            'LaGuardia Pl & W 3 St'
        ],
        'usertype': [
            'Subscriber', 'Subscriber', 'Subscriber', 'Subscriber', 'Subscriber',
            'Customer', 'Customer', 'Subscriber', 'Customer', 'Subscriber'
        ],
        'birth_year': [1983.0, 1983.0, 1988.0, 1987.0, 1986.0, 1990.0, 1992.0, 1985.0, 1989.0, 1984.0],
        'gender': [1, 1, 1, 1, 2, 1, 2, 1, 2, 1]
    })


class MinimalFailingWidget(PolarsBuckarooInfiniteWidget):
    """
    MINIMAL REPRODUCTION: 
    The exact set of analysis classes that triggers the polars mode() error.
    This is the smallest possible set that reproduces the citibike failure.
    """
    analysis_klasses = [
        VCAnalysis, 
        BasicAnalysis, 
        PlTyping, 
        ComputedDefaultSummaryStats, 
        HistogramAnalysis,
        DefaultSummaryStatsStyling, 
        DefaultMainStyling
    ]


def test_citibike_minimal_failure():
    """
    Original test that reproduces the citibike polars mode() error.
    """
    minimal_df = get_test_data()
    widget = PolarsBuckarooInfiniteWidget(minimal_df, debug=True)


def test_minimal_failing_reproduction():
    """
    MINIMAL REPRODUCTION: 
    This test isolates the exact minimal set of analysis classes that trigger 
    the polars mode() error. This should fail with:
    
    ERROR executing clause .rename_alias(selector.mode()): Series length 4 doesn't match the DataFrame height of 10
    """
    minimal_df = get_test_data()
    widget = MinimalFailingWidget(minimal_df, debug=True) 