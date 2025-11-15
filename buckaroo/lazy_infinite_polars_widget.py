#!/usr/bin/env python
# coding: utf-8
from __future__ import annotations

from typing import Any, Dict, List, Optional, Type
from io import BytesIO
from pathlib import Path

import anywidget
import polars as pl
from traitlets import Dict as TDict, Unicode, observe

from .dataflow.column_executor_dataflow import ColumnExecutorDataflow
from .customizations.polars_analysis import PL_Analysis_Klasses
from .pluggable_analysis_framework.polars_analysis_management import PolarsAnalysis
from .df_util import old_col_new_col
from .serialization_utils import pd_to_obj
from .customizations.polars_analysis import HistogramAnalysis as _H



class LazyInfinitePolarsBuckarooWidget(anywidget.AnyWidget):
    """
    A lazy, infinite-viewer widget for Polars LazyFrame built on ColumnExecutorDataflow.
    - Summary stats via ColumnExecutorDataflow + PAF executor
    - Infinite row streaming directly from the LazyFrame
    - Minimal DFViewer config (no code interpreter/post-processing)
    """

    _esm = Path(__file__).parent / "static" / "widget.js"
    _css = Path(__file__).parent / "static" / "compiled.css"
    render_func_name = Unicode("DFViewerInfinite").tag(sync=True)

    # Traits consumed by DFViewerInfiniteDS
    df_meta = TDict({
        'columns': 0,
        'rows_shown': 0,
        'filtered_rows': 0,
        'total_rows': 0
    }).tag(sync=True)
    df_data_dict = TDict({'empty': []}).tag(sync=True)
    df_display_args = TDict({}).tag(sync=True)
    df_id = Unicode("unknown").tag(sync=True)

    # Progress from executor (plumbed via listener)
    executor_progress = TDict({}).tag(sync=True)

    def __init__(
        self,
        ldf: pl.LazyFrame,
        *,
        analysis_klasses: Optional[List[Type[PolarsAnalysis]]] = None,
        debug: bool = False,
        column_executor_class: Optional[type] = None,
    ) -> None:
        super().__init__()
        self._debug = debug
        self._ldf = ldf
        default_analyses = PL_Analysis_Klasses

        self._analyses = list(analysis_klasses) if analysis_klasses is not None else default_analyses

        # Build stable rewrites
        all_cols = self._ldf.collect_schema().names()
        empty_pl_df = pl.DataFrame({c: [] for c in all_cols})
        self._orig_to_rw = dict(old_col_new_col(empty_pl_df))
        self._rw_to_orig = {v: k for k, v in self._orig_to_rw.items()}

        # Dataflow for summary stats
        self._df = ColumnExecutorDataflow(ldf, analysis_klasses=self._analyses,
                                          column_executor_class=column_executor_class)
        self.df_meta = self._df.df_meta

        # Compute summary stats and wire progress to a trait
        def _listener(note):
            # Minimal progress surface; expand as needed
            self.executor_progress = {
                'success': note.success,
                'col_group': note.col_group,
                'message': note.failure_message or ''
            }

        # Background by default: start with empty all_stats and minimal column config
        self.df_data_dict = {'main': [], 'all_stats': [], 'empty': []}
        df_viewer_config = {
            "pinned_rows": [],
            "column_config": self._build_column_config_from_schema(),
            "left_col_configs": [{"col_name": "index", "header_name": "index", "displayer_args": {"displayer": "obj"}}],
        }
        self.df_display_args = {
            'main': {
                'data_key': 'main',
                'df_viewer_config': df_viewer_config,
                'summary_stats_key': 'all_stats'
            }
        }

        import threading
        # Hook dataflow listener to update this widget's df_data_dict incrementally
        def _progress_update(aggregated_summary: Dict[str, Dict[str, Any]]) -> None:
            try:
                summary_rows = self._summary_to_rows(aggregated_summary)
                self.df_data_dict = {'main': [], 'all_stats': summary_rows, 'empty': []}
            except Exception:
                pass
        self._df.progress_update_callback = _progress_update

        def _bg():
            summary_sd = self._df.compute_summary_with_executor(progress_listener=_listener)
            summary_rows = self._summary_to_rows(summary_sd)
            self.df_data_dict = {'main': [], 'all_stats': summary_rows, 'empty': []}
            # update column config after summary (headers from summary)
            new_dfvc = dict(self.df_display_args['main']['df_viewer_config'])
            new_dfvc['column_config'] = self._build_column_config(summary_sd)
            self.df_display_args = {'main': dict(self.df_display_args['main'], df_viewer_config=new_dfvc)}
        threading.Thread(target=_bg, daemon=True).start()

        self.df_id = str(id(ldf))

        # Message bridge for infinite requests
        def payload_bridge(_unused_self, msg, _unused_buffers):
            if msg.get('type') == 'infinite_request':
                payload_args = msg['payload_args']
                self._handle_payload_args(payload_args)
        self.on_msg(payload_bridge)

    def _build_column_config(self, summary: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        column_config: List[Dict[str, Any]] = []
        for rw, meta in summary.items():
            col_name = rw
            header_name = str(meta.get('orig_col_name', rw))
            # Minimal displayers; could be improved using dtype if available
            column_config.append({
                "col_name": col_name,
                "header_name": header_name,
                "displayer_args": {"displayer": "obj"},
            })
        return column_config

    def _build_column_config_from_schema(self) -> List[Dict[str, Any]]:
        column_config: List[Dict[str, Any]] = []
        for orig, rw in self._orig_to_rw.items():
            column_config.append({
                "col_name": rw,
                "header_name": str(orig),
                "displayer_args": {"displayer": "obj"},
            })
        return column_config

    def _summary_to_rows(self, summary: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        import pandas as pd
        if not summary:
            return []
        df = pd.DataFrame(summary)
        return pd_to_obj(df)

    def _build_column_config(self, summary: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        column_config: List[Dict[str, Any]] = []
        for rw, meta in summary.items():
            col_name = rw
            header_name = str(meta.get('orig_col_name', rw))
            # Minimal displayers; could be improved using dtype if available
            column_config.append({
                "col_name": col_name,
                "header_name": header_name,
                "displayer_args": {"displayer": "obj"},
            })
        return column_config

    def _prepare_df_for_serialization(self, df: pl.DataFrame) -> pl.DataFrame:
        # Ensure 'index' present and rename data columns to rewritten names
        if 'index' not in df.columns:
            df = df.with_row_index(name='index')
        select_clauses: List[pl.Expr] = [pl.col('index')]
        for orig in self._orig_to_rw.keys():
            if orig in df.columns:
                rw = self._orig_to_rw.get(orig, orig)
                select_clauses.append(pl.col(orig).alias(rw))
        return df.select(select_clauses)

    def _to_parquet(self, df: pl.DataFrame) -> bytes:
        out = BytesIO()
        self._prepare_df_for_serialization(df).write_parquet(out, compression='uncompressed')
        out.seek(0)
        return out.read()

    def _handle_payload_args(self, new_payload_args: Dict[str, Any]) -> None:
        start, end = new_payload_args.get('start', 0), new_payload_args.get('end', 0)
        if start is None or end is None:
            return
        try:
            # create a derived lazyframe to avoid borrowing conflicts with background tasks
            base = self._ldf.select(pl.all())
            sort = new_payload_args.get('sort')
            if sort:
                orig_sort_col = self._rw_to_orig.get(sort, sort)
                sort_dir = new_payload_args.get('sort_direction')
                ascending = (sort_dir == 'asc')
                base = base.sort(orig_sort_col, descending=not ascending)
            slice_len = max(int(end) - int(start), 0)
            slice_df = base.slice(int(start), slice_len).with_row_index(name='index').collect()
            self.send({"type": "infinite_resp", 'key': new_payload_args, 'data': [], 'length': self.df_meta['total_rows']},
                      [self._to_parquet(slice_df)])

            second_pa = new_payload_args.get('second_request')
            if second_pa:
                s2, e2 = second_pa.get('start'), second_pa.get('end')
                if s2 is not None and e2 is not None:
                    slice2 = base.slice(int(s2), max(int(e2) - int(s2), 0)).with_row_index(name='index').collect()
                    self.send({"type": "infinite_resp", 'key': second_pa, 'data': [], 'length': self.df_meta['total_rows']},
                              [self._to_parquet(slice2)])
        except Exception as e:
            import traceback
            stack_trace = traceback.format_exc()
            self.send({"type": "infinite_resp", 'key': new_payload_args, 'data': [], 'error_info': stack_trace, 'length': 0}, [])


