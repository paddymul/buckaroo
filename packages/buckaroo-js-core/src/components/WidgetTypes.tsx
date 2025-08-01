export interface DFMeta {
    // static,
    total_rows: number;
    columns: number;
    filtered_rows: number;
    rows_shown: number;
}

export interface BuckarooOptions {
    sampled: string[];
    cleaning_method: string[];
    post_processing: string[];
    df_display: string[]; // keys into Into df_display_args
    show_commands: string[];
}

export type QuickAtom = number | string;
export type QuickArg = QuickAtom[];
export interface BuckarooState {
    sampled: string | false;
    cleaning_method: string | false;
    quick_command_args: Record<string, QuickArg>;
    post_processing: string | false;
    df_display: string; //at least one dataframe must always be displayed
    show_commands: string | false;
}

export type BKeys = "sampled" | "cleaning_method" | "post_processing" | "df_display";

// df_dict: Record<string, DFWhole>;
// df_meta: DFMeta;
/*

  df_dict: Record<string, DFWhole>;
  df_meta: DFMeta;
  operations: Operation[];
  on_operations: (ops: Operation[]) => void;
  operation_results: OperationResult;
  commandConfig: CommandConfigT;
  buckaroo_state: BuckarooState;
  on_buckaroo_state: React.Dispatch<React.SetStateAction<BuckarooState>>;
  buckaroo_options: BuckarooOptions;
*/
