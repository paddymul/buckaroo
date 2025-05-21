import { Operation, OperationEventFunc } from './OperationUtils';
import { ActualArg, CommandArgSpec } from './CommandUtils';
export declare const OperationDetail: ({ command, setCommand, columns, commandPatterns, }: {
    command: Operation;
    setCommand: OperationEventFunc;
    columns: string[];
    commandPatterns: CommandArgSpec;
}) => import("react/jsx-runtime").JSX.Element;
export declare const ArgGetters: ({ command, fullPattern, setCommand, columns, }: {
    command: Operation;
    fullPattern: ActualArg[];
    setCommand: OperationEventFunc;
    columns: string[];
}) => import("react/jsx-runtime").JSX.Element;
