import type { Meta, StoryObj } from "@storybook/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { DFViewerInfinite } from "../components/DFViewerParts/DFViewerInfinite";
import { ShadowDomWrapper } from "./StoryUtils";
import { DFViewerConfig, NormalColumnConfig } from "../components/DFViewerParts/DFWhole";
import { createDatasourceWrapper, createRawDataWrapper } from "../components/DFViewerParts/DFViewerDataHelper";

type TranscriptEvent =
  | { ts: number; event: "pinned_rows_config"; pinned_keys: string[]; cfg: any }
  | { ts: number; event: "all_stats_update"; len: number; sample: any; all_stats: any[] }
  | { ts: number; event: "custom_msg"; msg: any; buffers_len: number }
  // DFViewerInfinite diagnostics
  | { ts: number; event: "dfi_cols_fields"; fields: string[] }
  | { ts: number; event: "dfi_pinned_extracted"; pinned_keys: string[]; summary_len: number; top_len: number }
  | { ts: number; event: "dfi_pinned_sample"; sample: any }
  | { ts: number; event: "dfi_pinned_apply"; len: number; applied_first: any }
  | { ts: number; event: "dfi_grid_ready"; pinned_count: number | null; pinned_first: any }
  | { ts: number; event: "dfi_first_data_rendered"; pinned_count: number | null; pinned_first: any }
  // Datasource + parsed rows
  | { ts: number; event: "ds_request"; args: any }
  | { ts: number; event: "ds_success"; args: any; rows_len: number; total_len: number }
  | { ts: number; event: "infinite_resp_parsed"; key: any; rows_len: number; total_len: number; rows?: any[] };

const idxCol: NormalColumnConfig = {
  col_name: "index",
  header_name: "index",
  displayer_args: { displayer: "obj" },
};
const objCol = (name: string): NormalColumnConfig => ({
  col_name: name,
  header_name: name,
  displayer_args: { displayer: "obj" },
});

const baseConfig: DFViewerConfig = {
  column_config: [objCol("a"), objCol("b")],
  left_col_configs: [idxCol],
  pinned_rows: [
    { primary_key_val: "null_count", displayer_args: { displayer: "obj" } },
    { primary_key_val: "empty_count", displayer_args: { displayer: "obj" } },
  ],
};

//window._buckarooTranscript =
const PinnedRowsTranscriptReplayerInner = () => {
  const [summary, setSummary] = useState<any[]>([]);
  const [cfg, setCfg] = useState<DFViewerConfig>(baseConfig);
  const [rawRows, setRawRows] = useState<any[]>([]);
  const eventsRef = useRef<TranscriptEvent[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const data_wrapper = useMemo(() => {
    // Prefer exact rows from transcript if available; otherwise start empty DataSource(0 rows)
    if (rawRows && rawRows.length > 0) {
      return createRawDataWrapper(rawRows);
    }
    return createDatasourceWrapper([], 0);
  }, [rawRows]);

  useEffect(() => {
    // pull transcript from the window if present
    // @ts-ignore
    const t: TranscriptEvent[] = (window as any)._buckarooTranscript || [];
    eventsRef.current = Array.isArray(t) ? t.slice() : [];
  }, []);

  const start = () => {
    if (isRunning) return;
    setIsRunning(true);
    const evs = eventsRef.current.slice().sort((a, b) => a.ts - b.ts);
    const t0 = evs.length ? evs[0].ts : Date.now();
    const MIN_STEP_MS = 120; // ensure visible separation even if timestamps are identical
    let lastOffset = 0;
    evs.forEach((ev) => {
      let offset = ev.ts - t0;
      if (offset <= lastOffset) {
        offset = lastOffset + MIN_STEP_MS;
      }
      lastOffset = offset;
      setTimeout(() => {
        if (ev.event === "pinned_rows_config") {
          const keys = ev.pinned_keys || [];
          setCfg((old) => ({
            ...old,
            pinned_rows: keys.map((k) => ({ primary_key_val: k, displayer_args: { displayer: "obj" } })),
          }));
        } else if (ev.event === "dfi_cols_fields") {
          const fields = ev.fields || [];
          const dataFields = fields.filter((f) => f && f !== "index");
          setCfg((old) => ({
            ...old,
            column_config: dataFields.map((f) => objCol(f)),
            left_col_configs: [idxCol],
          }));
        } else if (ev.event === "all_stats_update") {
          // Deep-clone to break identity and make BigInt JSON-safe
          const safe = (function toJsonSafe(val: any): any {
            if (typeof val === "bigint") return val.toString();
            if (Array.isArray(val)) return val.map((v) => toJsonSafe(v));
            if (val && typeof val === "object") {
              const out: Record<string, any> = {};
              for (const k in val) {
                try {
                  out[k] = toJsonSafe(val[k]);
                } catch {
                  out[k] = null;
                }
              }
              return out;
            }
            return val;
          })(ev.all_stats || []);
          setSummary(safe);
        } else if (ev.event === "infinite_resp_parsed" && ev.rows && Array.isArray(ev.rows)) {
          // Use the exact rows parsed from the transcript
          const rows = ev.rows as any[];
          setRawRows(Array.isArray(rows) ? rows : []);
        } else if (ev.event === "ds_success") {
          // If no rows captured yet but datasource succeeded, at least switch to an empty Raw set to clear "None"
          if (rawRows.length === 0) setRawRows([]);
        }
      }, offset);
    });
  };

  return (
    <ShadowDomWrapper>
      <div style={{ width: 760 }}>
        <p style={{ marginBottom: 8 }}>
          Replays a captured transcript (window._buckarooTranscript) of model updates and custom messages,
          applying pinned row config, summary updates (all_stats), and simulating infinite responses by
          switching to 5 visible rows. Click Start after running the Jupyter widget with transcript logging
          enabled to reproduce the behavior here.
        </p>
        <div style={{ marginBottom: 8 }}>
          <button onClick={start} disabled={isRunning}>
            Start Replay
          </button>
          <span style={{ marginLeft: 12 }}>events: {eventsRef.current.length}</span>
        </div>
        <div style={{ height: 420 }}>
          <DFViewerInfinite
            data_wrapper={data_wrapper}
            df_viewer_config={cfg}
            summary_stats_data={summary}
            activeCol={["a", "a"]}
            setActiveCol={() => {}}
            outside_df_params={{}}
          />
        </div>
      </div>
    </ShadowDomWrapper>
  );
};

const meta = {
  title: "Buckaroo/DFViewer/PinnedRowsTranscriptReplayer",
  component: PinnedRowsTranscriptReplayerInner,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
} satisfies Meta<typeof PinnedRowsTranscriptReplayerInner>;

export default meta;
type Story = StoryObj<typeof meta>;
export const Primary: Story = { args: {} };


