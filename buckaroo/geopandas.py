rom buckaroo.customizations.styling import DefaultMainStyling, obj_, StylingAnalysis
class GeoStyling(StylingAnalysis): #DefaultMainStyling):
    requires_summary = [#"histogram", 
                        "is_numeric", "dtype", "_type"]
    @classmethod
    def style_column(kls, col:str, column_metadata):
        t = column_metadata['_type']
        if t == 'obj':
            return {'col_name':col, 'displayer_args': {'displayer': 'string', 'max_length': 100}}
        else:
            return DefaultMainStyling.style_column(col, column_metadata)
    pinned_rows = [obj_('dtype'), obj_('_type')]
    
from buckaroo.serialization_utils import pd_to_obj
from buckaroo.customizations.analysis import (TypingStats, ComputedDefaultSummaryStats, DefaultSummaryStats)

class GeopandasBuckarooWidget(buckaroo.BuckarooWidget):
    analysis_klasses = [
        TypingStats, #DefaultSummaryStats,
        #ComputedDefaultSummaryStats,
        GeoStyling
        #DefaultSummaryStatsStyling, DefaultMainStyling   
    ]
    def _df_to_obj(self, df):
        # I want to this, but then row numbers are lost
        #return pd_to_obj(self.sampling_klass.serialize_sample(df).to_pandas())
        pd_df = pd.DataFrame(dict(zip(df.columns, df.to_numpy().T)))
        return pd_to_obj(self.sampling_klass.serialize_sample(pd_df))


    
import pandas as pd
import buckaroo
#gdf = geopandas.GeoDataFrame.from_features(geojson)
def render_geopandas(gp_df):
    import geopandas
    
    geo_columns = []
    svg_columns = []
    columns = gp_df.columns.copy()
    for col in gp_df.columns:
        ser = gp_df[col]
        if isinstance(ser.dtype, geopandas.array.GeometryDtype):
            svg_col_name = col+"_svg"
            geo_columns.append(col)
            svg_columns.append(svg_col_name)
            gp_df[svg_col_name] = ser.apply(lambda x: x._repr_svg_())
    
    df = pd.DataFrame(dict(zip(gp_df.columns, gp_df.to_numpy().T)))

    col_config_override = {}
    for column in geo_columns:
       col_config_override[column] = {'merge_rule': 'hidden'}
    for column in svg_columns:
       col_config_override[column] = {'displayer_args': {'displayer': 'SVGDisplayer'}}
    svg_columns.extend(columns)
    #print(svg_columns)
    return buckaroo.BuckarooWidget(df[svg_columns], column_config_overrides=col_config_override, 
                                   pinned_rows=[],
                                   extra_grid_config={'rowHeight':105})
#bw = render_geopandas(gdf)
#bw
