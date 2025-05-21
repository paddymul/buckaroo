import { StoryObj } from '@storybook/react';
declare const meta: {
    title: string;
    component: ({ a }: {
        a: number;
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
