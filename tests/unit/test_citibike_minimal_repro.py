# state:READONLY
"""
Minimal reproduction of the citibike_df failure.

This test reproduces the specific polars error:
ERROR executing clause .rename_alias(selector.mode()): Series: ["tripduration", "most_freq"], 
length 1 doesn't match the DataFrame height of 10
"""

import polars as pl
from buckaroo.polars_buckaroo import PolarsBuckarooInfiniteWidget


def test_citibike_minimal_failure():
    """
    Minimal test that reproduces the citibike polars mode() error.
    
    This test creates a small DataFrame with the same characteristics as the citibike
    dataset that cause the mode() operation to fail. The test should fail with the
    polars error about Series length not matching DataFrame height.
    """
    # Create a minimal DataFrame that reproduces the same issue
    # The key issue is having diverse data types that trigger the mode() analysis
    minimal_df = pl.DataFrame({
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
    
    # This should fail with the polars mode() error
    widget = PolarsBuckarooInfiniteWidget(minimal_df, debug=True) 