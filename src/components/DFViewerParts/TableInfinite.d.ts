import { PayloadArgs } from './gridUtils';
import { Operation } from '../OperationUtils';
import { PayloadResponse } from './SmartRowCache';
export declare const InfiniteWrapper: ({ payloadArgs, on_payloadArgs, payloadResponse, operations, }: {
    payloadArgs: PayloadArgs;
    on_payloadArgs: (pa: PayloadArgs) => void;
    payloadResponse: PayloadResponse;
    operations: Operation[];
}) => import("react/jsx-runtime").JSX.Element;
export declare const InfiniteEx: () => import("react/jsx-runtime").JSX.Element;
