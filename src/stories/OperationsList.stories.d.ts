import { StoryObj } from '@storybook/react';
import { Operation } from '../components/OperationUtils';
declare const meta: {
    title: string;
    component: ({ operations }: {
        operations: Operation[];
    }) => import("react/jsx-runtime").JSX.Element;
    parameters: {
        layout: string;
    };
    tags: string[];
};
export default meta;
type Story = StoryObj<typeof meta>;
export declare const Default: Story;
export declare const Empty: Story;
export declare const SingleOperation: Story;
export declare const DataCleaning: Story;
export declare const ManyOperations: Story;
