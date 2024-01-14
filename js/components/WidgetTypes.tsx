
export interface DFMeta {
  // static,
  total_rows: number;
  columns: number;
  rows_shown: number;
}export interface BuckarooOptions {
  sampled: string[];
  summary_stats: string[];
  show_commands: string[];
  auto_clean: string[];
  reorderd_columns: string[];
}
export interface BuckarooState {
  sampled: string | false;
  summary_stats: string | false; // there could be multiple
  show_commands: string | false;
  auto_clean: string | false;
  reorderd_columns: string | false;
  search_string: string;
}

export type BKeys = keyof BuckarooOptions;

  // df_dict: Record<string, DFWhole>;
  // df_meta: DFMeta;


  df_dict: Record<string, DFWhole>;
  df_meta: DFMeta;
  operations: Operation[];
  on_operations: (ops: Operation[]) => void;
  operation_results: OperationResult;
  commandConfig: CommandConfigT;
  buckaroo_state: BuckarooState;
  on_buckaroo_state: React.Dispatch<React.SetStateAction<BuckarooState>>;
  buckaroo_options: BuckarooOptions;
