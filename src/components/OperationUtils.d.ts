import { SymbolT, ColEnumArgs, SymbolDf } from './CommandUtils';
export declare const sym: (symbolName: string) => {
    symbol: string;
};
export type Atom = number | string | SymbolT | ColEnumArgs;
export type SettableArg = number | string | ColEnumArgs;
export type OperationSingleColumn = [SymbolT, SymbolDf, string];
export type OperationSingleArg = [SymbolT, SymbolDf, string, Atom];
export type OperationTwoArg = [SymbolT, SymbolDf, string, Atom, Atom];
export type Operation = OperationSingleColumn | OperationSingleArg | OperationTwoArg;
export declare const getOperationKey: (ops: Operation[], idx: number) => string;
export type SetOperationFunc = (newCommand: Operation) => void;
export type SetOperationsFunc = (newCommands: Operation[]) => void;
export type OperationDefaultArgs = Record<string, Operation>;
export declare const bakedOperations: Operation[];
export type OperationEventFunc = (newCommand: Operation) => void;
export type NoArgEventFunc = () => void;
