import { StoryObj } from '@storybook/react';
import { DFViewerConfig } from '../components/DFViewerParts/DFWhole';
declare const meta: {
    title: string;
    component: ({ data, df_viewer_config, secondary_df_viewer_config, summary_stats_data, outside_df_params, }: {
        data: any[];
        df_viewer_config: DFViewerConfig;
        secondary_df_viewer_config?: DFViewerConfig;
        summary_stats_data?: any[];
        outside_df_params?: any;
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
export declare const Large: Story;
export declare const PinnedRows: Story;
export declare const ColorMapExample: Story;
export declare const MedDFVHeight: Story;
