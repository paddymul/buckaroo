import { StoryObj } from '@storybook/react';
import { DFViewerConfig } from '../components/DFViewerParts/DFWhole';
import { SetColumnFunc } from '../components/DFViewerParts/gridUtils';
import { DatasourceOrRaw } from '../components/DFViewerParts/DFViewerDataHelper';
declare const meta: {
    title: string;
    component: ({ data_wrapper, df_viewer_config, summary_stats_data, activeCol, setActiveCol, outside_df_params, error_info, }: {
        data_wrapper: DatasourceOrRaw;
        df_viewer_config: DFViewerConfig;
        summary_stats_data?: any[];
        activeCol?: [string, string];
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
