import { StoryObj } from '@storybook/react';
import { Operation } from '../components/OperationUtils';
import { CommandConfigT } from '../components/CommandUtils';
declare const meta: {
    title: string;
    component: ({ operations, activeColumn, allColumns, command_config, }: {
        operations: Operation[];
        activeColumn: string;
        allColumns: string[];
        command_config: CommandConfigT;
    }) => import("react/jsx-runtime").JSX.Element;
    parameters: {
        layout: string;
    };
    tags: string[];
    argTypes: {};
};
export default meta;
type Story = StoryObj<typeof meta>;
export declare const Default: Story;
export declare const Empty: Story;
export declare const SingleOperation: Story;
export declare const DataCleaning: Story;
export declare const ManyOperations: Story;
