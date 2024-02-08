from buckaroo.dataflow_traditional import StylingAnalysis


def obj_(pkey):
    return {'primary_key_val': pkey, 'displayer_args': { 'displayer': 'obj' } }

def float_(pkey, digits=3):
    return {'primary_key_val': pkey, 
            'displayer_args': { 'displayer': 'float', 'minimumFractionDigits':digits, 'maximumFractionDigits':digits}}


class DefaultMainStyling(StylingAnalysis):
    requires_summary = ["histogram", "is_numeric", "dtype", "is_integer"]
    pinned_rows = [
        obj_('dtype'),
        {'primary_key_val': 'histogram', 'displayer_args': { 'displayer': 'histogram' }}]

    @classmethod
    def style_column(kls, col, sd):
        #print(col, list(sd.keys()))
        if len(sd.keys()) == 0:
            #I'm still having problems with index and polars
            return {'col_name':col, 'displayer_args': {'displayer': 'obj'}}
        digits = 3
        if sd['is_integer']:
            disp = {'displayer': 'float', 'min_fraction_digits':0, 'max_fraction_digits':0}
        elif sd['is_numeric']:
            disp = {'displayer': 'float', 'min_fraction_digits':digits, 'max_fraction_digits':digits}
        else:
            disp = {'displayer': 'obj'}
        return {'col_name':col, 'displayer_args': disp }


class DefaultSummaryStatsStyling(StylingAnalysis):
    pinned_rows = [
        obj_('dtype'),
        float_('min'),
        #float_('median'),
        float_('mean'),
        float_('max'),
        float_('unique_count', 0),
        float_('distinct_count', 0),
        float_('empty_count', 0)
    ]
    df_display_name = "summary"
    data_key = "empty"
    summary_stats_key= 'all_stats'
