import { StoryObj } from '@storybook/react';
import { MessageBox } from '../components/MessageBox';
declare const meta: {
    title: string;
    component: typeof MessageBox;
    parameters: {
        layout: string;
    };
    tags: string[];
    argTypes: {
        messages: {
            control: "object";
            description: string;
        };
    };
};
export default meta;
type Story = StoryObj<typeof meta>;
export declare const Empty: Story;
export declare const CacheMessages: Story;
export declare const CacheInfo: Story;
export declare const ExecutionUpdates: Story;
export declare const MixedMessages: Story;
export declare const ManyMessages: Story;
export declare const LongMessages: Story;
export declare const StreamingMessages: Story;
