import * as React from "react";
import * as ReactDOM from "react-dom/client";
import { useState } from "react";
import srt from "buckaroo-js-core";
import "./widget.css";
import "../buckaroo-js-core/dist/style.css";



/**
 * @template {Record<string, any>} T
 * @typedef RenderContext
 * @property {import("@anywidget/types").AnyModel<T>} model
 * @property {import("@anywidget/types").Experimental} experimental
 */

/** @type {React.Context<RenderContext<any>>} */
let RenderContext = React.createContext(/** @type {any} */ (null));

/**
 * @returns {RenderContext<any>}
 */
function useRenderContext() {
	let ctx = React.useContext(RenderContext);
	if (!ctx) throw new Error("RenderContext not found");
	return ctx;
}

/**
 * @template {Record<string, any>} T
 * @returns {import("@anywidget/types").AnyModel<T>}
 */
export function useModel() {
	let ctx = useRenderContext();
	return ctx.model;
}

/** @returns {import("@anywidget/types").Experimental} */
export function useExperimental() {
	let ctx = useRenderContext();
	return ctx.experimental;
}


/**
 * A React Hook to use model-backed state in a component.
 *
 * Mirrors the API of `React.useState`, but synchronizes state with
 * the underlying model provded by an anywidget host.
 *
 * @example
 * ```ts
 * import * as React from "react";
 * import { useModelState } from "@anywidget/react";
 *
 * function Counter() {
 *   let [value, setValue] = useModelState<number>("value");
 *
 *   return (
 *     <button onClick={() => setValue((v) => v + 1)}>
 *       Count: {value}
 *     </button>
 *   );
 * }
 * ```
 *
 * @template S
 * @param {string} key - The name of the model field to use
 * @returns {[S, React.Dispatch<React.SetStateAction<S>>]}
 */
export function useModelState(key) {
	let model = useModel();
	let value = React.useSyncExternalStore(
		(update) => {
			model.on(`change:${key}`, update);
			return () => model.off(`change:${key}`, update);
		},
		() => model.get(key),
	);
	/** @type {React.Dispatch<React.SetStateAction<S>>} */
	let setValue = React.useCallback(
		(value) => {
			model.set(
				key,
				// @ts-expect-error - TS cannot correctly narrow type
				typeof value === "function" ? value(model.get(key)) : value,
			);
			model.save_changes();
		},
		[model, key],
	);
	return [value, setValue];
}

//patched version of createRender that doesn't use strict mode
// increased performance and danger
function createRender(Widget) {
	return ({ el, model, experimental }) => {
		let root = ReactDOM.createRoot(el);
		root.render(
				React.createElement(
					RenderContext.Provider,
					{ value: { model, experimental } },
					React.createElement(Widget),
				),
		);
		return () => root.unmount();
	};
}

const renderDFV = createRender(() => {
	console.log("renderDFV");
	const [df_data, _set_df_meta] = useModelState("df_data");
	const [df_viewer_config, _set_dfvc] = useModelState("df_viewer_config");
	const [summary_stats_data, _set_ssd] = useModelState("summary_stats_data");
	console.log("df_data", df_data);
	console.log("df_viewer_config", df_viewer_config);
	console.log("summary_stats_data", summary_stats_data);
	return (
		<div className="buckaroo_anywidget">
			<srt.DFViewer
				df_data={df_data}
				df_viewer_config={df_viewer_config}
				summary_stats_data={summary_stats_data}
			/>
		</div>
	);
});

const renderBuckarooWidget = createRender(() => {
	const model = useModel();
	const [df_data_dict, _set_df_data_dict] = useModelState("df_data_dict");
	const [df_display_args, _set_dda] = useModelState("df_display_args");
	const [df_meta, _set_df_meta] = useModelState("df_meta");
	// Diagnostics: log all_stats shape and pinned_rows config when they change
	// Also persist to window._buckarooTranscript for replay in Storybook
	// FIXME: Feature-flag the transcript recording via a Python trait (e.g. enable_transcript_recording)
	// so it only records when explicitly enabled, not all the time
	React.useEffect(() => {
		try {
			const allStats = (df_data_dict && df_data_dict['all_stats']) || [];
			// eslint-disable-next-line no-console
			console.info(
				"[WidgetTSX][Model] df_data_dict all_stats len",
				allStats.length,
				"sample",
				allStats[0] || null,
			);
			// Persist transcript for replay
			// @ts-ignore
			window._buckarooTranscript = window._buckarooTranscript || [];
			// @ts-ignore
			window._buckarooTranscript.push({
				ts: Date.now(),
				event: "all_stats_update",
				len: allStats.length,
				sample: allStats[0] || null,
				all_stats: allStats,
			});
		} catch {}
	}, [df_data_dict]);
	React.useEffect(() => {
		try {
			const pr = df_display_args?.main?.df_viewer_config?.pinned_rows || [];
			// eslint-disable-next-line no-console
			console.info(
				"[WidgetTSX][Model] pinned_rows",
				pr.map((x:any)=>x?.primary_key_val),
			);
			// @ts-ignore
			window._buckarooTranscript = window._buckarooTranscript || [];
			// @ts-ignore
			window._buckarooTranscript.push({
				ts: Date.now(),
				event: "pinned_rows_config",
				pinned_keys: pr.map((x:any)=>x?.primary_key_val),
				cfg: df_display_args?.main?.df_viewer_config || {},
			});
			// Derive DFViewerInfinite-like transcript (columns and pinned extraction) from model state
			const cfg = df_display_args?.main?.df_viewer_config;
			if (cfg) {
				const left = Array.isArray(cfg.left_col_configs) ? cfg.left_col_configs : [];
				const cols = Array.isArray(cfg.column_config) ? cfg.column_config : [];
				const fieldOf = (c: any) =>
					(typeof c?.field === "string" && c.field) || (typeof c?.col_name === "string" ? c.col_name : undefined);
				const leftFields = left.map(fieldOf).filter(Boolean);
				const dataFields = cols.map(fieldOf).filter(Boolean);
				const allFields = ([] as any[]).concat(leftFields, dataFields);
				// eslint-disable-next-line no-console
				console.info("[WidgetTSX][DFI] fields", allFields);
				// @ts-ignore
				window._buckarooTranscript.push({
					ts: Date.now(),
					event: "dfi_cols_fields",
					fields: allFields,
				});
				const allStats = ((df_data_dict && (df_data_dict as any)['all_stats']) || []) as any[];
				const pinnedKeys = pr.map((p: any) => p?.primary_key_val).filter(Boolean);
				const findRow = (k: any) =>
					allStats.find((r) => r && (r.index === k || r.level_0 === k)) || null;
				const topRows = pinnedKeys.map(findRow).filter(Boolean);
				// eslint-disable-next-line no-console
				console.info("[WidgetTSX][DFI] pinned extracted", {
					keys: pinnedKeys,
					summaryLen: allStats.length,
					topLen: topRows.length,
				});
				// @ts-ignore
				window._buckarooTranscript.push({
					ts: Date.now(),
					event: "dfi_pinned_extracted",
					pinned_keys: pinnedKeys,
					summary_len: allStats.length,
					top_len: topRows.length,
				});
				if (topRows.length > 0) {
					// eslint-disable-next-line no-console
					console.debug("[WidgetTSX][DFI] pinned sample", topRows[0]);
					// @ts-ignore
					window._buckarooTranscript.push({
						ts: Date.now(),
						event: "dfi_pinned_sample",
						sample: topRows[0],
					});
				}
			}
		} catch {}
	}, [df_display_args, df_data_dict]);
	// Capture custom messages from Python (e.g., infinite_resp) into transcript
	React.useEffect(() => {
		const handler = (msg: any, buffers?: ArrayBuffer[]) => {
			try {
				// eslint-disable-next-line no-console
				console.info("[WidgetTSX][CustomMsg]", msg?.type, msg);
				// @ts-ignore
				window._buckarooTranscript = window._buckarooTranscript || [];
				// @ts-ignore
				window._buckarooTranscript.push({
					ts: Date.now(),
					event: "custom_msg",
					msg,
					buffers_len: buffers?.length || 0,
				});
				// If this is an infinite_resp with a parquet buffer, try to parse it
				if (msg && msg.type === "infinite_resp" && buffers && buffers.length > 0 && buffers[0] instanceof ArrayBuffer) {
					(async () => {
						try {
							// @ts-ignore dynamic import
							const mod = await import("hyparquet");
							const parquetMetadata = (mod as any).parquetMetadata;
							const parquetRead = (mod as any).parquetRead;
							const buf = buffers[0] as ArrayBuffer;
							const metadata = parquetMetadata(buf);
							parquetRead({
								file: buf,
								metadata,
								rowFormat: "object",
								onComplete: (rows: any[]) => {
									const toJsonSafe = (val: any): any => {
										if (typeof val === "bigint") return val.toString();
										if (Array.isArray(val)) return val.map(toJsonSafe);
										if (val && typeof val === "object") {
											const out: any = {};
											for (const k in val) {
												try { out[k] = toJsonSafe(val[k]); } catch { out[k] = null; }
											}
											return out;
										}
										return val;
									};
									// @ts-ignore
									window._buckarooTranscript.push({
										ts: Date.now(),
										event: "infinite_resp_parsed",
										key: (msg as any).key || null,
										rows_len: Array.isArray(rows) ? rows.length : 0,
										total_len: (msg as any).length ?? null,
										rows: toJsonSafe(rows || []),
									});
								},
							});
						} catch (e) {
							console.warn("[WidgetTSX][CustomMsg] failed to parse parquet buffer", e);
							// @ts-ignore
							window._buckarooTranscript.push({
								ts: Date.now(),
								event: "infinite_resp_buf",
								key: (msg as any).key || null,
								buffers_len: buffers?.length || 0,
							});
						}
					})();
				}
			} catch {}
		};
		// @ts-ignore backbone event from anywidget
		model.on("msg:custom", handler);
		return () => {
			// @ts-ignore
			model.off("msg:custom", handler);
		};
	}, [model]);

	const [operations, on_operations] = useModelState("operations");
	const [operation_results, _set_opr] = useModelState("operation_results");
	const [command_config, _set_cc] = useModelState("command_config");

	const [buckaroo_state, on_buckaroo_state] = useModelState("buckaroo_state");
	const [buckaroo_options, _set_boptions] = useModelState("buckaroo_options");
	return (
		<div className="buckaroo_anywidget">
			<srt.WidgetDCFCell
				df_data_dict={df_data_dict}
				df_display_args={df_display_args}
				df_meta={df_meta}
				operations={operations}
				on_operations={on_operations}
				operation_results={operation_results}
				command_config={command_config}
				buckaroo_state={buckaroo_state}
				on_buckaroo_state={on_buckaroo_state}
				buckaroo_options={buckaroo_options}
			/>
		</div>
	);
});

const srcClosureRBI = (src) => {
    const renderBuckarooInfiniteWidget = createRender((a,b,c) => {
	const model = useModel()
	const [df_data_dict, _set_df_data_dict] = useModelState("df_data_dict");
	const [df_display_args, _set_dda] = useModelState("df_display_args");
	const [df_meta, _set_df_meta] = useModelState("df_meta");

	const [operations, on_operations] = useModelState("operations");
	const [operation_results, _set_opr] = useModelState("operation_results");
	const [command_config, _set_cc] = useModelState("command_config");
	const [buckaroo_state, on_buckaroo_state] = useModelState("buckaroo_state");
	const [buckaroo_options, _set_boptions] = useModelState("buckaroo_options");

	// FIXME: Feature-flag the transcript recording via a Python trait
	// Capture custom messages (infinite_resp) into transcript for debugging/replay
	React.useEffect(() => {
		const handler = (msg: any, buffers?: ArrayBuffer[]) => {
			try {
				// eslint-disable-next-line no-console
				console.info("[WidgetTSX][InfiniteWidget][CustomMsg]", msg?.type, msg);
				// @ts-ignore
				window._buckarooTranscript = window._buckarooTranscript || [];
				// @ts-ignore
				window._buckarooTranscript.push({
					ts: Date.now(),
					event: "custom_msg",
					msg,
					buffers_len: buffers?.length || 0,
				});
				// Parse infinite_resp parquet buffers
				if (msg && msg.type === "infinite_resp" && buffers && buffers.length > 0 && buffers[0] instanceof ArrayBuffer) {
					(async () => {
						try {
							// @ts-ignore dynamic import
							const mod = await import("hyparquet");
							const parquetMetadata = (mod as any).parquetMetadata;
							const parquetRead = (mod as any).parquetRead;
							const buf = buffers[0] as ArrayBuffer;
							const metadata = parquetMetadata(buf);
							parquetRead({
								file: buf,
								metadata,
								rowFormat: "object",
								onComplete: (rows: any[]) => {
									const toJsonSafe = (val: any): any => {
										if (typeof val === "bigint") return val.toString();
										if (Array.isArray(val)) return val.map(toJsonSafe);
										if (val && typeof val === "object") {
											const out: any = {};
											for (const k in val) {
												try { out[k] = toJsonSafe(val[k]); } catch { out[k] = null; }
											}
											return out;
										}
										return val;
									};
									// @ts-ignore
									window._buckarooTranscript.push({
										ts: Date.now(),
										event: "infinite_resp_parsed",
										key: (msg as any).key || null,
										rows_len: Array.isArray(rows) ? rows.length : 0,
										total_len: (msg as any).length ?? null,
										rows: toJsonSafe(rows || []),
									});
								},
							});
						} catch (e) {
							console.warn("[WidgetTSX][InfiniteWidget] failed to parse parquet buffer", e);
						}
					})();
				}
			} catch {}
		};
		// @ts-ignore backbone event from anywidget
		model.on("msg:custom", handler);
		return () => {
			// @ts-ignore
			model.off("msg:custom", handler);
		};
	}, [model]);

	return (
	    <div className="buckaroo_anywidget">
	    <srt.BuckarooInfiniteWidget
	    
	    df_data_dict={df_data_dict}
	    df_display_args={df_display_args}
	    df_meta={df_meta}
	    operations={operations}
	    on_operations={on_operations}
	    operation_results={operation_results}
	    command_config={command_config}
	    buckaroo_state={buckaroo_state}
	    on_buckaroo_state={on_buckaroo_state}
	    buckaroo_options={buckaroo_options}
	    src={src}
		/>
		</div>
	);
    });

    const renderDFViewerInfiniteWidget = createRender((a,b,c) => {
	const model = useModel()
	const [df_meta, _set_df_meta] = useModelState("df_meta");
	  const [df_data_dict, _set_df_data_dict] = useModelState("df_data_dict");
      // df_data_dict ready
	const [df_display_args, _set_dda] = useModelState("df_display_args");
        const [df_id, _set_df_id] = useModelState("df_id");
	const [message_log, _set_message_log] = useModelState("message_log");
	const [show_message_box, _set_show_message_box] = useModelState("show_message_box");
	return (
	    <div className="buckaroo_anywidget">
		<srt.DFViewerInfiniteDS
                    df_meta={df_meta}
                    df_data_dict={df_data_dict}
                    df_display_args={df_display_args}
                    df_id={df_id}
	            src={src}
		    message_log={message_log}
		    show_message_box={show_message_box}
		/>
		</div>
	);
    });

    return [renderBuckarooInfiniteWidget, renderDFViewerInfiniteWidget];
}

export default async () => {
    let extraState = {};
    return {
	initialize({ model }) {
	    // we only want to create KeyAwareSmartRowCache once, it caches sourceName too
	    // so having it live between relaods is key
	    //const [respError, setRespError] = useState<string | undefined>(undefined);
	    const setRespError = (a,b) => {console.log("setRespError",a,b);}
	    extraState['keySmartCache'] = srt.getKeySmartRowCache(model, setRespError);
	    const [renderBuckarooInfinite, renderDFViewerInfinite] = srcClosureRBI(extraState['keySmartCache']);
	    extraState['renderBuckarooInfinite'] = renderBuckarooInfinite;
	    extraState['renderDFViewerInfinite'] = renderDFViewerInfinite;
	},
	render({ model, el, experimental }) {
	    const render_func_name = model.get("render_func_name");
	    if (render_func_name === "DFViewer") {
		renderDFV({ el, model, experimental });
	    } else if (render_func_name === "BuckarooWidget") {
		renderBuckarooWidget({ el, model, experimental });
	    } else if (render_func_name === "BuckarooInfiniteWidget") {
		extraState['renderBuckarooInfinite']({ el, model, experimental });
	    } else if (render_func_name === "DFViewerInfinite") {
		extraState['renderDFViewerInfinite']({ el, model, experimental });
	    }
	}
    }
}

