import type { Meta, StoryObj } from "@storybook/react";
import { DFViewerInfinite } from "../components/DFViewerParts/DFViewerInfinite";
import { DFViewerConfig } from "../components/DFViewerParts/DFWhole";
import { SetColumFunc } from "../components/DFViewerParts/gridUtils";
import { ShadowDomWrapper } from "./StoryUtils";
import { DatasourceWrapper, createDatasourceWrapper, dictOfArraystoDFData, arange, NRandom, HistogramSummaryStats } from "../components/DFViewerParts/DFViewerDataHelper";

const DFViewerInfiniteWrap = ({
    data,
    df_viewer_config,
    summary_stats_data,
    activeCol,
    setActiveCol,
    outside_df_params,
    error_info,
}: {
    data: any[];
    df_viewer_config: DFViewerConfig;
    summary_stats_data?: any[];
    activeCol?: string;
    setActiveCol?: SetColumFunc;
    outside_df_params?: any;
    error_info?: string;
}) => {
  const data_wrapper: DatasourceWrapper = createDatasourceWrapper(data);
  return (
    <ShadowDomWrapper>
     <div style={{height:500, width:800}}>
      <DFViewerInfinite
      data_wrapper={data_wrapper}
      df_viewer_config={df_viewer_config}
      summary_stats_data={summary_stats_data}
      activeCol={activeCol}
      setActiveCol={setActiveCol}
      outside_df_params={outside_df_params}
      error_info={error_info} />
     </div>
     </ShadowDomWrapper>);
}

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories#default-export
const meta = {
  title: "Buckaroo/DFViewer/DFViewerInfiniteShadow",
  component: DFViewerInfiniteWrap,
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
    {'a':30, 'b':"bar"},
    {'a':NaN, 'b':NaN},
    {'a':null, 'b':null},
    {'a':undefined, 'b':undefined}

  ];

export const Primary: Story = {
  args: {
    //@ts-ignore
    // the undefineds aren't allowed in the type but do happen in the wild
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
      {
        col_name: 'b',
        displayer_args: {
          displayer: 'string',
        },
      }
    ],
    pinned_rows:[]
  },
  
    }
}




const N = 10_000;
console.log("156")
console.log(dictOfArraystoDFData({'a':NRandom(N, 3,50), 'b':arange(N)   }))

export const Large: Story = {
  args: {
    data: dictOfArraystoDFData({'a':NRandom(N, 3,50), 'b':arange(N)}),
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


export const PinnedRows: Story = {
  args: {
    data: [], //dictOfArraystoDFData({'a':NRandom(N, 3,50), 'b':arange(N)   }),
    df_viewer_config: {
      column_config: [

        {
          col_name: 'a',
          displayer_args: {
            displayer: 'obj',
          },
        },
        {
          col_name: 'b',
          displayer_args: {
            displayer: 'obj',
          },
        },
        {
          col_name: 'c',
          displayer_args: {
            displayer: 'obj',
          },
        },
        {
          col_name: 'd',
          displayer_args: {
            displayer: 'obj',
          },
        },
      ],
      pinned_rows: [{
        'primary_key_val': 'histogram',
        'displayer_args': { 'displayer': 'histogram' }
      }]
    },
    summary_stats_data: HistogramSummaryStats

  }
}



const MEDIUM= 300;

export const MedDFVHeight: Story = {
  args: {
    data:dictOfArraystoDFData({'a':NRandom(MEDIUM, 3,50), 'b':arange(MEDIUM)   }),
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
    pinned_rows:[],
    component_config: {dfvHeight:200}
  },
  
    }
}