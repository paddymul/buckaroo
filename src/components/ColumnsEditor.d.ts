import { DFViewerConfig } from './DFViewerParts/DFWhole';
import { Operation } from './OperationUtils';
import { CommandConfigT } from './CommandUtils';
import { OperationResult } from './DependentTabs';
export type OperationSetter = (ops: Operation[]) => void;
export interface WidgetConfig {
    showCommands: boolean;
}
export declare function ColumnsEditor({ df_viewer_config, activeColumn, operations, setOperations, operation_result, command_config, }: {
    df_viewer_config: DFViewerConfig;
    activeColumn: string;
    operations: Operation[];
    setOperations: OperationSetter;
    operation_result: OperationResult;
    command_config: CommandConfigT;
}): import("react/jsx-runtime").JSX.Element;
