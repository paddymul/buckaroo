import type { Meta, StoryObj } from "@storybook/react";
import { DatasourceWrapper, DFViewerInfinite, RawDataWrapper } from "../components/DFViewerParts/DFViewerInfinite";
import { DFData, DFViewerConfig } from "../components/DFViewerParts/DFWhole";
import { SetColumFunc } from "../components/DFViewerParts/DFViewer";
//import "../packages/buckaroo-js-core/dist/style.css";
import "../style/dcf-npm.css"
import '@ag-grid-community/styles/ag-grid.css'; 
import '@ag-grid-community/styles/ag-theme-quartz.css';
import { IDatasource, IGetRowsParams } from "@ag-grid-community/core";

const DFViewerInfiniteWrap = ({
    data,
    df_viewer_config,
    summary_stats_data,
    activeCol,
    setActiveCol,
    outside_df_params,
    error_info,
}: {
    data: DFData;
    df_viewer_config: DFViewerConfig;
    summary_stats_data?: DFData;
    activeCol?: string;
    setActiveCol?: SetColumFunc;
    // these are the parameters that could affect the table,
    // dfviewer doesn't need to understand them, but it does need to use
    // them as keys to get updated data
    outside_df_params?: any;
    error_info?: string;
}) => {

  const tempDataSource:IDatasource = {
    rowCount:data.length,
    getRows(params:IGetRowsParams) {
      const slicedData = data.slice(params.startRow, params.endRow);
      params.successCallback(slicedData, data.length)

    }
  };
  const data_wrapper:DatasourceWrapper = {
    datasource:tempDataSource,
    data_type:"DataSource",
    length:data.length
  }
  return (
     <div style={{height:500, width:800}}>
      <DFViewerInfinite
      data_wrapper={data_wrapper}
      df_viewer_config={df_viewer_config}
      summary_stats_data={summary_stats_data}
      activeCol={activeCol}
      setActiveCol={setActiveCol}
      outside_df_params={outside_df_params}
      error_info={error_info} />
     </div>);
}

    

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories#default-export
const meta = {
  title: "Buckaroo/DFViewer/DFViewerInfinite",
  component:DFViewerInfiniteWrap,
  parameters: {
    // Optional parameter to center the component in the Canvas. More
    // info: https://storybook.js.org/docs/configure/story-layout
    layout: "centered",
      
  },
  // This component will have an automatically generated Autodocs
  // entry: https://storybook.js.org/docs/writing-docs/autodocs
  tags: ["autodocs"],
  // More on argTypes: https://storybook.js.org/docs/api/argtypes
  argTypes: {
      //backgroundColor: { control: "color" },
      //operations: 
  },
  // Use `fn` to spy on the onClick arg, which will appear in the
  // actions panel once invoked:
  // https://storybook.js.org/docs/essentials/actions#action-args
  //args: { onClick: fn() },
} satisfies Meta<typeof DFViewerInfiniteWrap>;

export default meta;
type Story = StoryObj<typeof meta>;
const data = [
    {'a':20, 'b':"foo"},
    {'a':30, 'b':"bar"}
  ];

export const Primary: Story = {
  args: {
    data:data,
    df_viewer_config: {
      column_config: [
      {
        col_name: 'a',
        displayer_args: {
          displayer: 'float',
          min_fraction_digits: 2,
          max_fraction_digits: 8,
        },
        //tooltip_config: { tooltip_type: 'summary_series' },
      },
      {
        col_name: 'a',
        displayer_args: {
          displayer: 'integer',
          min_digits:2, max_digits:3
        },
      },
      {
        col_name: 'b',
        displayer_args: {
          displayer: 'obj',
        },
      },
    ],
    pinned_rows:[]
  },
  
    }
}
