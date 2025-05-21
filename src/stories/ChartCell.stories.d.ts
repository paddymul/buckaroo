import { StoryObj } from '@storybook/react';
import { ChartDisplayerA } from '../components/DFViewerParts/DFWhole';
declare const meta: {
    title: string;
    component: ({ value, dispArgs }: {
        value: any;
        dispArgs: ChartDisplayerA;
    }) => import("react/jsx-runtime").JSX.Element;
    parameters: {
        layout: string;
    };
    tags: string[];
    argTypes: {};
};
export default meta;
type Story = StoryObj<typeof meta>;
export declare const Primary: Story;
export declare const Area: Story;
export declare const Composed: Story;
export declare const ComposedCustomColor: Story;
