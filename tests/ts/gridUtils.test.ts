//import { add, multiply } from "../src/math";

import { extractSDFT } from "../../js/components/DFViewer";
import { DFData } from "../../js/components/DFWhole";

describe("Math functions", () => {

  it("should convert to expected format", () => {
    const basicSDF:DFData = [
      {'index': 'histogram_bins',     'a':[2,3]},
      {'index': 'histogram_log_bins', 'a':[20,30], 'b': [10, 20]
    },
    ];
    const expected = {
      'a': {'histogram_bins': [2,3], 'histogram_log_bins': [20, 30]},
      'b': {'histogram_bins': [],    'histogram_log_bins': [10, 20]}
    };
    const result = extractSDFT(basicSDF);
    expect(result).toEqual(expected);


  });
});

