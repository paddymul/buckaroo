from buckaroo import BuckarooWidget
from buckaroo.buckaroo_widget import RawDFViewerWidget
from buckaroo.dataflow.widget_extension_utils import configure_buckaroo

def SolaraDFViewer(df, column_config_overrides=None,
                    extra_pinned_rows=None, pinned_rows=None,
                    extra_analysis_klasses=None, analysis_klasses=None):
    import reacton    
    BuckarooKls = configure_buckaroo(
        BuckarooWidget,
        extra_pinned_rows=extra_pinned_rows, pinned_rows=pinned_rows,
        extra_analysis_klasses=extra_analysis_klasses, analysis_klasses=analysis_klasses)

    bw = BuckarooKls(df, column_config_overrides=column_config_overrides)
    dfv_config = bw.df_display_args['dfviewer_special']['df_viewer_config']
    df_data = bw.df_data_dict['main']
    summary_stats_data = bw.df_data_dict['all_stats']

    comp = reacton.core.ComponentWidget(widget=RawDFViewerWidget)
    
    element_kwargs = dict(df_data=df_data, df_viewer_config=dfv_config, summary_stats_data=summary_stats_data)

    return reacton.core.Element(comp, kwargs=element_kwargs)

def SolaraBuckarooWidget(df, column_config_overrides=None,
                    extra_pinned_rows=None, pinned_rows=None,
                    extra_analysis_klasses=None, analysis_klasses=None):
    import reacton    
    BuckarooKls = configure_buckaroo(
        BuckarooWidget,
        extra_pinned_rows=extra_pinned_rows, pinned_rows=pinned_rows,
        extra_analysis_klasses=extra_analysis_klasses, analysis_klasses=analysis_klasses)

    comp = reacton.core.ComponentWidget(widget=BuckarooKls)
    return reacton.core.Element(comp, df=df, column_config_overrides=column_config_overrides)



def bw_klass_to_dfv_component(BuckarooKls):
    import reacton
    def df_responding_component(df, column_config_overrides=None):

        bw = BuckarooKls(df, column_config_overrides=column_config_overrides)
        dfv_config = bw.df_display_args['dfviewer_special']['df_viewer_config']
        df_data = bw.df_data_dict['main']
        summary_stats_data = bw.df_data_dict['all_stats']
        dfv_comp = reacton.core.ComponentWidget(widget=RawDFViewerWidget)
        element_kwargs = dict(
            df_data=df_data, df_viewer_config=dfv_config, summary_stats_data=summary_stats_data)

        return reacton.core.Element(dfv_comp, kwargs=element_kwargs)


        # I'm still not quite sure on state management, filed a bug against solara asking for clarification
        # https://github.com/widgetti/solara/issues/542

        # it might help to make just a RawDFViewer solara component
        
        # buckaroo_state, set_buckaroo_state = solara.use_state(bw.buckaroo_state)
        # return reacton.core.Element(dfv_comp, kwargs=element_kwargs), bw.buckaroo_options, bw.buckaroo_state

    return df_responding_component


def bw_klass_to_dfv_component(BuckarooKls):
    import reacton
    def df_responding_component(df, column_config_overrides=None):

        bw = BuckarooKls(df, column_config_overrides=column_config_overrides)
        dfv_config = bw.df_display_args['dfviewer_special']['df_viewer_config']
        df_data = bw.df_data_dict['main']
        summary_stats_data = bw.df_data_dict['all_stats']
        dfv_comp = reacton.core.ComponentWidget(widget=RawDFViewerWidget)
        element_kwargs = dict(
            df_data=df_data, df_viewer_config=dfv_config, summary_stats_data=summary_stats_data)
    return df_responding_component



def SolaraPolarsDFViewer(df, column_config_overrides=None,
                    extra_pinned_rows=None, pinned_rows=None,
                    extra_analysis_klasses=None, analysis_klasses=None):
    from buckaroo.polars_buckaroo import PolarsBuckarooWidget
    BuckarooKls = configure_buckaroo(
        PolarsBuckarooWidget,
        extra_pinned_rows=extra_pinned_rows, pinned_rows=pinned_rows,
        extra_analysis_klasses=extra_analysis_klasses, analysis_klasses=analysis_klasses)
    dfv_comp = bw_klass_to_dfv_component(BuckarooKls)
    return dfv_comp(df, column_config_overrides)


def SolaraPolarsBuckarooWidget(df, column_config_overrides=None,
                    extra_pinned_rows=None, pinned_rows=None,
                    extra_analysis_klasses=None, analysis_klasses=None):
    import reacton
    from buckaroo.polars_buckaroo import PolarsBuckarooWidget
    BuckarooKls = configure_buckaroo(
        PolarsBuckarooWidget,
        extra_pinned_rows=extra_pinned_rows, pinned_rows=pinned_rows,
        extra_analysis_klasses=extra_analysis_klasses, analysis_klasses=analysis_klasses)

    comp = reacton.core.ComponentWidget(widget=BuckarooKls)
    return reacton.core.Element(comp, df=df, column_config_overrides=column_config_overrides)
    

def SolaraHeadlessBuckaroo(df, column_config_overrides=None,
                    extra_pinned_rows=None, pinned_rows=None,
                    extra_analysis_klasses=None, analysis_klasses=None):
    import reacton
    from buckaroo.polars_buckaroo import PolarsBuckarooWidget
    BuckarooKls = configure_buckaroo(
        PolarsBuckarooWidget,
        extra_pinned_rows=extra_pinned_rows, pinned_rows=pinned_rows,
        extra_analysis_klasses=extra_analysis_klasses, analysis_klasses=analysis_klasses)

    bw = BuckarooKls(df, column_config_overrides=column_config_overrides)
    dfv_config = bw.df_display_args['dfviewer_special']['df_viewer_config']
    df_data = bw.df_data_dict['main']
    summary_stats_data = bw.df_data_dict['all_stats']

    comp = reacton.core.ComponentWidget(widget=RawDFViewerWidget)
    
    element_kwargs = dict(df_data=df_data, df_viewer_config=dfv_config, summary_stats_data=summary_stats_data)

    return reacton.core.Element(comp, kwargs=element_kwargs)
