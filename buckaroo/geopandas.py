import pandas as pd
import buckaroo

from buckaroo.customizations.styling import DefaultMainStyling, obj_, StylingAnalysis
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import ColAnalysis
from buckaroo.serialization_utils import pd_to_obj

class SvgReprPostProcessing(ColAnalysis):
    @classmethod
    def post_process_df(kls, gdf):
        geo_columns = []
        svg_columns = []
        columns = gdf.columns.copy()
        svg_ser_dict = {}
        for col in gdf.columns:
            ser = gdf[col]
            if isinstance(ser.dtype, geopandas.array.GeometryDtype):
                svg_col_name = col+"_svg"
                geo_columns.append(col)
                svg_columns.append(svg_col_name)
                svg_ser_dict[svg_col_name] = ser.apply(lambda x: x._repr_svg_())
        svg_df = pd.DataFrame(svg_ser_dict)
        merged_df = pd.concat([svg_df, gdf], axis=1)
        
        extra_conf = {}
        for col in svg_columns:
            extra_conf[col] = {'column_config_override': {'displayer_args': {'displayer': 'SVGDisplayer'}}}
        return merged_df, extra_conf
    post_processing_method = "svg_geo"
    
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
    pinned_rows = [
        #obj_('dtype'), obj_('_type')
    ]
    

class GeopandasBuckarooWidget(buckaroo.BuckarooWidget):
    analysis_klasses = [
        TypingStats,
        GeoStyling,
        SvgReprPostProcessing]
    
    def _df_to_obj(self, df):
        pd_df = pd.DataFrame(dict(zip(df.columns, df.to_numpy().T)))
        return pd_to_obj(self.sampling_klass.serialize_sample(pd_df))
