import logging
from typing import Iterable, TypedDict, Union, List, Dict, Any, Literal
from typing_extensions import NotRequired, TypeAlias

import pandas as pd
from buckaroo.df_util import ColIdentifier
from buckaroo.pluggable_analysis_framework.col_analysis import (ColAnalysis, ColMeta, SDType)

logger = logging.getLogger()

# Cell Renderer Types
HistogramDisplayerA = TypedDict('HistogramDisplayerA', {'displayer': Literal["histogram"]})
ChartDisplayerA = TypedDict('ChartDisplayerA', {'displayer': Literal["chart"]})
LinkifyDisplayerA = TypedDict('LinkifyDisplayerA', {'displayer': Literal["linkify"]})
BooleanCheckboxDisplayerA = TypedDict('BooleanCheckboxDisplayerA', {'displayer': Literal["boolean_checkbox"]})
Base64PNGImageDisplayerA = TypedDict('Base64PNGImageDisplayerA', {'displayer': Literal["Base64PNGImageDisplayer"]})
SVGDisplayerA = TypedDict('SVGDisplayerA', {'displayer': Literal["SVGDisplayer"]})

CellRendererArgs = Union[
    HistogramDisplayerA,
    ChartDisplayerA,
    LinkifyDisplayerA,
    BooleanCheckboxDisplayerA,
    Base64PNGImageDisplayerA,
    SVGDisplayerA
]

# Formatter Types
ObjDisplayerA = TypedDict('ObjDisplayerA', {
    'displayer': Literal["obj"],
    'max_length': NotRequired[int]
})

BooleanDisplayerA = TypedDict('BooleanDisplayerA', {
    'displayer': Literal["boolean"]
})

StringDisplayerA = TypedDict('StringDisplayerA', {
    'displayer': Literal["string"],
    'max_length': NotRequired[int]
})

FloatDisplayerA = TypedDict('FloatDisplayerA', {
    'displayer': Literal["float"],
    'min_fraction_digits': int,
    'max_fraction_digits': int
})

DatetimeDefaultDisplayerA = TypedDict('DatetimeDefaultDisplayerA', {
    'displayer': Literal["datetimeDefault"]
})

DatetimeLocaleDisplayerA = TypedDict('DatetimeLocaleDisplayerA', {
    'displayer': Literal["datetimeLocaleString"],
    'locale': Literal["en-US", "en-GB", "en-CA", "fr-FR", "es-ES", "de-DE", "ja-JP"],
    'args': Dict[str, Any]
})

IntegerDisplayerA = TypedDict('IntegerDisplayerA', {
    'displayer': Literal["integer"],
    'min_digits': int,
    'max_digits': int
})

FormatterArgs = Union[
    ObjDisplayerA,
    BooleanDisplayerA,
    StringDisplayerA,
    FloatDisplayerA,
    DatetimeDefaultDisplayerA,
    DatetimeLocaleDisplayerA,
    IntegerDisplayerA
]

# Combined displayer types
DisplayerArgs = Union[FormatterArgs, CellRendererArgs]

# Color mapping types
ColorMap = Union[Literal["BLUE_TO_YELLOW", "DIVERGING_RED_WHITE_BLUE"], List[str]]

ColorMapRules = TypedDict('ColorMapRules', {
    'color_rule': Literal["color_map"],
    'map_name': ColorMap,
    'val_column': NotRequired[str]
})

ColorCategoricalRules = TypedDict('ColorCategoricalRules', {
    'color_rule': Literal["color_categorical"],
    'map_name': ColorMap,
    'val_column': NotRequired[str]
})

ColorWhenNotNullRules = TypedDict('ColorWhenNotNullRules', {
    'color_rule': Literal["color_not_null"],
    'conditional_color': Union[str, Literal["red"]],
    'exist_column': str
})

ColorFromColumn = TypedDict('ColorFromColumn', {
    'color_rule': Literal["color_from_column"],
    'val_column': str
})

ColorMappingConfig = Union[
    ColorMapRules,
    ColorWhenNotNullRules,
    ColorFromColumn,
    ColorCategoricalRules
]

# Tooltip types
SimpleTooltip = TypedDict('SimpleTooltip', {
    'tooltip_type': Literal["simple"],
    'val_column': str
})

SummarySeriesTooltip = TypedDict('SummarySeriesTooltip', {
    'tooltip_type': Literal["summary_series"]
})

TooltipConfig = Union[SimpleTooltip, SummarySeriesTooltip]

# Column config types
BaseColumnConfig = TypedDict('BaseColumnConfig', {
    'displayer_args': DisplayerArgs,
    'color_map_config': NotRequired[ColorMappingConfig],
    'tooltip_config': NotRequired[TooltipConfig],
    'ag_grid_specs': NotRequired[Dict[str, Any]]  # AGGrid_ColDef
})

NormalColumnConfig = TypedDict('NormalColumnConfig', {
    'col_name': str,
    'displayer_args': DisplayerArgs,
    'color_map_config': NotRequired[ColorMappingConfig],
    'tooltip_config': NotRequired[TooltipConfig],
    'ag_grid_specs': NotRequired[Dict[str, Any]]  # AGGrid_ColDef
})

MultiIndexColumnConfig = TypedDict('MultiIndexColumnConfig', {
    'col_path': List[str],
    'field': str,
    'displayer_args': DisplayerArgs,
    'color_map_config': NotRequired[ColorMappingConfig],
    'tooltip_config': NotRequired[TooltipConfig],
    'ag_grid_specs': NotRequired[Dict[str, Any]]  # AGGrid_ColDef
})
ColumnConfig = Union[NormalColumnConfig, MultiIndexColumnConfig]


PinnedRowConfig = TypedDict('PinnedRowConfig', {
    'primary_key_val': str,
    'displayer_args': DisplayerArgs,
    'default_renderer_columns': NotRequired[List[str]]  # used to render index column values with string not the specified displayer
})

ComponentConfig = TypedDict('ComponentConfig', {
    'height_fraction': NotRequired[float],
    'dfvHeight': NotRequired[int],  # temporary debugging prop
    'layoutType': NotRequired[Literal["autoHeight", "normal"]],
    'shortMode': NotRequired[bool],
    'selectionBackground': NotRequired[str],
    'className': NotRequired[str]
})

DFViewerConfig = TypedDict('DFViewerConfig', {
    'pinned_rows': List[PinnedRowConfig],
    'column_config': List[ColumnConfig],
    'first_col_config': ColumnConfig,  # basically for the pandas index
    'extra_grid_config': NotRequired[Dict[str, Any]],  # GridOptions
    'component_config': NotRequired[ComponentConfig]
})

DisplayArgs = TypedDict('DisplayArgs', {
    'data_key':str,
    'df_viewer_config':DFViewerConfig,
    'summary_stats_key': str})

EMPTY_DFVIEWER_CONFIG: DFViewerConfig = {
    'pinned_rows': [],
    'column_config': [],
    'first_col_config': {'col_name': 'index',
                       'displayer_args': {'displayer': 'obj'}}
}


EMPTY_DF_DISPLAY_ARG: DisplayArgs = {
  'data_key': 'empty', 'df_viewer_config': EMPTY_DFVIEWER_CONFIG,
  'summary_stats_key': 'empty'}


SENTINEL_DF_1 = pd.DataFrame({'foo'  :[10, 20], 'bar' : ["asdf", "iii"]})
SENTINEL_DF_2 = pd.DataFrame({'col1' :[55, 55], 'col2': ["pppp", "333"]})


def merge_sds(*sds):
    """merge sds with later args taking precedence

    sub-merging of "overide_config"??
    """
    base_sd = {}
    for sd in sds:
        for column in sd.keys():
            base_sd[column] = merge_column(base_sd.get(column, {}), sd[column])
    return base_sd


def merge_column(base, new):
    """
    merge individual column dictionaries, with special handling for column_config_override
    """
    ret = base.copy()
    ret.update(new)

    base_override = base.get('column_config_override', {}).copy()
    new_override = new.get('column_config_override', {}).copy()
    base_override.update(new_override)

    if len(base_override) > 0:
        ret['column_config_override'] = base_override
    return ret


OverrideColumnConfig:TypeAlias = Dict[ColIdentifier, BaseColumnConfig]

def merge_column_config(styled_column_config:List[ColumnConfig], overide_column_configs:OverrideColumnConfig) -> List[ColumnConfig]:
    existing_column_config: List[ColumnConfig] = styled_column_config.copy()
    ret_column_config: List[ColumnConfig] = []
    for row in existing_column_config:
        if 'col_name' in row:
            # str necessary because sometimes numbers still come through
            col: ColIdentifier = str(row['col_name']) # typing: ignore  
        else:
            col: ColIdentifier = row['col_path']
            
        if col in overide_column_configs:
            row.update(overide_column_configs[col])
        if row.get('merge_rule', 'blank') == 'hidden':
            continue
        ret_column_config.append(row)
    return ret_column_config


def safedel(dct:Dict[str, Any], key:str) -> Dict[str, Any]:
    if key in dct:
        del dct[key]
    return dct
        

class StylingAnalysis(ColAnalysis):
    provides_defaults: ColMeta = {}
    pinned_rows:  List[PinnedRowConfig] = []
    extra_grid_config: NotRequired[Dict[str, Any]] = {}
    component_config: NotRequired[ComponentConfig] = {}
    
    @classmethod
    def style_column(cls, col:str, _column_metadata: ColMeta) -> BaseColumnConfig:
        """
          This is the method that should be overridden. by subclasses
        """
        return {'displayer_args': {'displayer': 'obj'}}

    parquet_style_index: bool = True

    @classmethod
    def get_index_name(cls, df:pd.DataFrame) -> str :
        if cls.parquet_style_index:
            #"('index', '')"
            if isinstance(df.columns, pd.MultiIndex):
                extra_len = df.columns.nlevels - 1
                new_index = ['index'] + [''] * extra_len
                return str(tuple(new_index))
        return 'index'

    
    @classmethod
    def fix_column_config(cls, col: Union[Iterable[str], str], base_cc:BaseColumnConfig) -> ColumnConfig:
        safedel(base_cc, 'col_name')
        safedel(base_cc, 'col_path')
        safedel(base_cc, 'field')
        if isinstance(col, tuple):
            base_cc['col_path'] = col
            base_cc['field'] = str(col)
        else:
            base_cc['col_name'] = str(col) # sometimes numbers still creep in here
        return base_cc
    
    #what is the key for this in the df_display_args_dictionary
    df_display_name: str = "main"
    data_key: str = "main"
    summary_stats_key: str = 'all_stats'

    @classmethod
    def default_styling(cls, col_name:Union[Iterable[str], str], /) -> ColumnConfig:
        return cls.fix_column_config(col_name, {'displayer_args': {'displayer': 'obj'}})

    @classmethod
    def get_dfviewer_config(cls, sd:SDType, df:pd.DataFrame) -> DFViewerConfig:
        index_config : ColumnConfig = cls.default_styling('index')
        return {
            'pinned_rows': cls.pinned_rows,
            'column_config': cls.style_columns(sd, df),
            'first_col_config':  index_config,
            'extra_grid_config': cls.extra_grid_config,
            'component_config': cls.component_config
        }

    
    @classmethod
    def style_columns(cls, sd:SDType, df:pd.DataFrame) -> List[ColumnConfig]:
        ret_col_config: List[ColumnConfig] = []
        #this is necessary for polars to add an index column, which is
        #required so that summary_stats makes sense
            
        for col, col_meta in sd.items():
            if col_meta.get('merge_rule', None) == 'hidden':
                continue
            try:

                #it actually gets tuples here
                base_style: ColumnConfig = cls.fix_column_config(col, cls.style_column(col, col_meta))
            except Exception as exc:
                if len(col_meta) == 0 and len(cls.requires_summary) > 0:
                    # this is called in instantiation without col_meta, and that can cause failures
                    # we want to just swallow these errors and not warn
                    pass
                else:
                    # something unexpected happened here, warn so that the develoepr is notified
                    logger.warn(f"Warning, styling failed from {cls} on column {col} with col_meta {col_meta} using default_styling instead")
                    logger.warn(exc)
                # Always provide a style, not providing a style
                # results in no display which is a very bad user
                # experience
                base_style = cls.default_styling(col)
            if 'column_config_override' in col_meta:
                #column_config_override, sent by the instantiation, gets set later

                cco: ColumnConfig = col_meta['column_config_override'] # pyright: ignore[reportAssignmentType]
                base_style.update(cco) # pyright: ignore[reportCallIssue, reportArgumentType]
            if base_style.get('merge_rule') == 'hidden':
                continue
            ret_col_config.append(base_style)
        return ret_col_config
    
