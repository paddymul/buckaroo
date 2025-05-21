import { Operation, SetOperationsFunc } from './OperationUtils';
import { CommandConfigT } from './CommandUtils';
export declare const OperationAdder: ({ column, addOperationCb, defaultArgs, }: {
    column: string;
    addOperationCb: any;
    defaultArgs: any;
}) => JSX.Element;
export declare const OperationViewer: ({ operations, setOperations, activeColumn, allColumns, command_config, }: {
    operations: Operation[];
    setOperations: SetOperationsFunc;
    activeColumn: string;
    allColumns: string[];
    command_config: CommandConfigT;
}) => import("react/jsx-runtime").JSX.Element;
