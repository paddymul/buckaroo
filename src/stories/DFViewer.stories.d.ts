import { StoryObj } from '@storybook/react';
import { DFData, DFViewerConfig } from '../components/DFViewerParts/DFWhole';
import { SetColumnFunc } from '../components/DFViewerParts/gridUtils';
declare const meta: {
    title: string;
    component: ({ df_data, df_viewer_config, summary_stats_data, activeCol, setActiveCol, }: {
        df_data: DFData;
        df_viewer_config: DFViewerConfig;
        summary_stats_data?: DFData;
        activeCol?: string;
        setActiveCol?: SetColumnFunc;
        outside_df_params?: any;
        error_info?: string;
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
export declare const Tooltip: Story;
export declare const ColorFromCol: Story;
export declare const Chart: Story;
