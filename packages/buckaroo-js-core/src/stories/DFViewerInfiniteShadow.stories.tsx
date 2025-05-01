import type { Meta, StoryObj } from "@storybook/react";
import { DFViewerInfinite } from "../components/DFViewerParts/DFViewerInfinite";
import { DFViewerConfig, ColumnConfig } from "../components/DFViewerParts/DFWhole";
import { SetColumFunc } from "../components/DFViewerParts/gridUtils";
import { ShadowDomWrapper } from "./StoryUtils";
import { DatasourceWrapper, createDatasourceWrapper, dictOfArraystoDFData, arange, NRandom, HistogramSummaryStats } from "../components/DFViewerParts/DFViewerDataHelper";
import { useState } from "react";

const objColumn = (col_name: string): ColumnConfig => ({
  col_name,
  displayer_args: {
    displayer: 'obj' as const,
  },
});

const floatColumn = (col_name: string, min_fraction_digits: number, max_fraction_digits: number): ColumnConfig => ({
  col_name,
  displayer_args: {
    displayer: 'float' as const,
    min_fraction_digits,
    max_fraction_digits,
  },
});

const integerColumn = (col_name: string, min_digits: number, max_digits: number): ColumnConfig => ({
  col_name,
  displayer_args: {
    displayer: 'integer' as const,
    min_digits,
    max_digits,
  },
});

const DFViewerInfiniteWrap = ({
    data,
    df_viewer_config,
    secondary_df_viewer_config,
    summary_stats_data,
    activeCol,
    setActiveCol,
    outside_df_params,
    error_info,
}: {
    data: any[];
    df_viewer_config: DFViewerConfig;
    secondary_df_viewer_config?: DFViewerConfig;
    summary_stats_data?: any[];
    activeCol?: string;
    setActiveCol?: SetColumFunc;
    outside_df_params?: any;
    error_info?: string;
}) => {
  const [useSecondaryConfig, setUseSecondaryConfig] = useState(false);
  const data_wrapper: DatasourceWrapper = createDatasourceWrapper(data);
  const activeConfig = useSecondaryConfig ? (secondary_df_viewer_config || df_viewer_config) : df_viewer_config;

  return (
    <ShadowDomWrapper>
     <div style={{height:500, width:800}}>
      <div style={{marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '10px'}}>
        <button 
          onClick={() => setUseSecondaryConfig(!useSecondaryConfig)}
        >
          Toggle Config
        </button>
        <span>Current Config: {useSecondaryConfig ? 'Secondary' : 'Primary'}</span>
      </div>
      <DFViewerInfinite
      data_wrapper={data_wrapper}
      df_viewer_config={activeConfig}
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

const primaryConfigPrimary:DFViewerConfig = {
      column_config: [
        floatColumn('a', 2, 8),
        integerColumn('a', 2, 3),
        objColumn('b'),
        {
          col_name: 'b',
          displayer_args: {
            displayer: 'string',
          },
        },
      ],
      pinned_rows: [],
   };
    const LargeConfig:DFViewerConfig = {
      column_config: [
      floatColumn('a', 2, 8),
      integerColumn('a', 2, 3),
      objColumn('b'),
    ],
        pinned_rows:[]
  }
  const PinnedRowConfig:DFViewerConfig = {
    column_config: [
      objColumn('a'),
      objColumn('b'),
      objColumn('c'),
      objColumn('d'),
    ],
    pinned_rows: [{
      'primary_key_val': 'histogram',
      'displayer_args': { 'displayer': 'histogram' }
    }]
  };
  const IntFloatConfig:DFViewerConfig =  {
    column_config: [
    floatColumn('a', 2, 8),
    integerColumn('a', 2, 3),
    objColumn('b'),
  ],
  pinned_rows:[],
  component_config: {dfvHeight:200}
};

export const Primary: Story = {
  args: {
    //@ts-ignore
    // the undefineds aren't allowed in the type but do happen in the wild
    data: data,
    df_viewer_config: primaryConfigPrimary,
    secondary_df_viewer_config:LargeConfig
  },
};

const N = 5_000;

export const Large: Story = {
  args: {
    data: dictOfArraystoDFData({'a':NRandom(N, 3,50), 'b':arange(N)}),
    df_viewer_config: LargeConfig,
    secondary_df_viewer_config: PinnedRowConfig,
    }

}


export const PinnedRows: Story = {
  args: {
    data: [], 
    df_viewer_config: PinnedRowConfig,
    secondary_df_viewer_config: IntFloatConfig,
    summary_stats_data: HistogramSummaryStats

  }
}



const MEDIUM= 300;

export const MedDFVHeight: Story = {
  args: {
    data:dictOfArraystoDFData({'a':NRandom(MEDIUM, 3,50), 'b':arange(MEDIUM)   }),
    df_viewer_config: IntFloatConfig,
    secondary_df_viewer_config: PinnedRowConfig,
    }
}