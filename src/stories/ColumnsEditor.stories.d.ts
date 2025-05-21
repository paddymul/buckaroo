import { StoryObj } from '@storybook/react';
import { ColumnsEditor } from '../components/ColumnsEditor';
declare const meta: {
    title: string;
    component: typeof ColumnsEditor;
    parameters: {
        layout: string;
    };
    tags: string[];
};
export default meta;
type Story = StoryObj<typeof meta> | any;
export declare const Default: Story;
export declare const Empty: Story;
export declare const SingleOperation: Story;
export declare const DataCleaning: Story;
export declare const ManyOperations: Story;
