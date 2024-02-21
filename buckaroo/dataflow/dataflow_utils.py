
def find_most_specific_styling(klasses, df_display_name):
    """if we have multiple styling klasses, all of which extend StylingAnalysis keyed to df_display_name='main'
    we want a deterministic result for which one is the called class to provide styling for that key

    if B extends A, B is more specific.

    Since most class extension for styling will work by extending
    DefaultMainStyling, try to follow the user's intent by making sure
    the most specific class is chosen

    https://stackoverflow.com/questions/23660447/how-can-i-sort-a-list-of-python-classes-by-inheritance-depth
    """

    

def configure_buckaroo(
        BaseBuckarooKls,
        column_config_overrides=None,
        extra_pinned_rows=None, pinned_rows=None,
        extra_analysis_klasses=None, analysis_klasses=None):
    """Used to instantiate a synthetic Buckaroo class with easier extension methods.

    It seemed more straight forward to write this as a completely
    separate function vs a classmethod so that things are clear vs
    inheritance
    """

    # In this case we are going to extend PolarsBuckarooWidget so we can take this combination with us
    base_a_klasses = BaseBuckarooKls.analysis_klasses.copy()
    if extra_analysis_klasses:
        if analysis_klasses is not None:
            raise Exception("Must specify either extra_analysis_klasses or analysis_klasses, not both")
        base_a_klasses.extend(extra_analysis_klasses)
    elif analysis_klasses:
        base_a_klasses = analysis_klasses


    #there could possibly be another way of picking off the styling
    #klass vs just knowing that it's default BaseStylingKls
    #BaseStylingKls = DefaultMainStyling 
    BaseStylingKls = find_most_specific_styling(DefaultMainStyling, 'main')

    base_pinned_rows = BaseStylingKls.pinned_rows.copy()
    if extra_pinned_rows:
        if pinned_rows is not None:
            raise Exception("Must specify either extra_pinned_rows or pinned_rows, not both")
        base_pinned_rows.extend(extra_pinned_rows)
    elif pinned_rows is not None: # is not None accomodates empty list
        base_pinned_rows = pinned_rows

    class SyntheticStyling(BaseStylingKls):
        pinned_rows = base_pinned_rows
        df_display_name = "dfviewer_special"
