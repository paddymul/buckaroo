//import { add, multiply } from "../src/math";

import { extractSDFT } from '../../js/components/gridUtils';
import { DFData } from "../../js/components/DFWhole";

describe("testing utility functions in gridUtils ", () => {
  // mostly sanity checks to help develop gridUtils

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
  it("color mapper should pick from ranges properly", () => {
    

  function getHistoIndex(val:number, histogram_edges:number[]): number {
    /*
  np.histogram([1, 2, 3, 4,  10, 20, 30, 40, 300, 300, 400, 500], bins=5)
( [  8,       0,     2,     1,     1], 
  [  1. , 100.8, 200.6, 300.4, 400.2, 500. ])
  The bottom matters for us, those are the endge
  
  this means that 8 values are between 1 and 100.8  and 2 values are between 200.6 and 300.4
    */
    if (histogram_edges.length == 0) {
      return 0;
    }
    for(let i=0; i<histogram_edges.length; i++) {
      if (val <= histogram_edges[i]) {
        return i;
      }
    }
    return histogram_edges.length;
  }
  const edges = [2, 4, 10, 30];

  expect(getHistoIndex(1,  [])).toBe(0);

  expect(getHistoIndex(1,  edges)).toBe(0);
  expect(getHistoIndex(3,  edges)).toBe(1);
  expect(getHistoIndex(5,  edges)).toBe(2);
  expect(getHistoIndex(10, edges)).toBe(2);
  expect(getHistoIndex(11, edges)).toBe(3);
  expect(getHistoIndex(11000, edges)).toBe(4);

  
  });
});

