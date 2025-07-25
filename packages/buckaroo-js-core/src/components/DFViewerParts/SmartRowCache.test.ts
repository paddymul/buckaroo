import * as _ from "lodash";
//import { describe, expect } from 'jest';
import {
    Segment,
    segmentLT,
    segmentBetween,
    segmentsOverlap,
    merge,
    mergeSegments,
    SegData,
    segmentSubset,
    getSliceRange,
    getRange,
    segmentsSize,
    segmentIntersect,
    compactSegments,
    SmartRowCache,
    minimumFillArgs,
    KeyAwareSmartRowCache,
    PayloadArgs,
    PayloadResponse,
    //    RequestFN
} from "./SmartRowCache"
import {
    DFData,
    DFDataRow
} from "./DFWhole";



const low:Segment = [20,30]
const mid:Segment = [ 25, 55];
const midBetween:Segment = [35, 45];
const high:Segment = [50, 100]
const around:Segment = [20,120]

describe('segment operators', () => {
    test('test segmentLT', () => {
	expect(segmentLT(low, high)).toBe(true);
	expect(segmentLT(high, low)).toBe(false);
	expect(segmentLT(high, high)).toBe(false);
	expect(segmentLT(around, high)).toBe(true); // because around starts before high
	expect(segmentLT(high, around)).toBe(false);

	expect(segmentLT(low, around)).toBe(true); // start at the same place, around ends higher
	expect(segmentLT(around, low)).toBe(false); // start at the same place, around ends higher

    });

    test('test segmentBetween', () => {
	expect(segmentBetween(around, low, high)).toBe(false);
	expect(segmentBetween(low, low, high)).toBe(false);
	expect(segmentBetween(midBetween, low, high)).toBe(true);
	expect(segmentBetween(midBetween, high, low)).toBe(true);
    });
    test('test segmentsOverlap', () => {
	expect(segmentsOverlap(low, high)).toBe(false);
	expect(segmentsOverlap(high, low)).toBe(false);
	expect(segmentsOverlap(high, high)).toBe(true);
	expect(segmentsOverlap(around, high)).toBe(true);

	expect(segmentsOverlap(mid, high)).toBe(true);
	expect(segmentsOverlap(low, mid)).toBe(true);
	expect(segmentsOverlap([0,20], [0,10])).toBe(true);
    });

    test('test segmentSubset', () => {
	expect(segmentSubset(low, high)).toBe(false);
	expect(segmentSubset(high, low)).toBe(false);
	expect(segmentSubset(around, high)).toBe(true);
	expect(segmentSubset(high, around)).toBe(false);

	expect(segmentSubset(mid, low)).toBe(false); // although they overlap, they aren't subsets
	expect(segmentSubset(low, mid)).toBe(false); // although they overlap, they aren't subsets

	expect(segmentSubset([0,20], [0,10])).toBe(true); // they start at same number, but the inner ends before
    });

    test('test segmentIntersect', () => {
	expect(segmentIntersect(around, high)).toStrictEqual(high);
	expect(segmentIntersect(high, around)).toStrictEqual(high);
	expect(segmentIntersect(mid, low)).toStrictEqual([25,30]);
	expect(segmentIntersect(low, mid)).toStrictEqual([25,30]);
    });

    test('test minimumFillArgs4', () => {
	//same start
	expect(minimumFillArgs([0,20], [0,30])).toStrictEqual({'start':20, 'end':30})
    })


    test('test minimumFillArgs', () => {
	expect(minimumFillArgs(mid, low)).toStrictEqual({'start':20, 'end':25})
    })
    test('test minimumFillArgs2', () => {
	expect(minimumFillArgs(low, mid)).toStrictEqual({'start':30, 'end':55})
    })

    test('test minimumFillArgs3', () => {
	expect(minimumFillArgs(low, high)).toStrictEqual({'start':50, 'end':100})
    })

    test('test minimumFillArgs nothing needed', () => {
	//nothing needed 
	expect(minimumFillArgs([0,30], [0,20])).toStrictEqual(true)
	expect(minimumFillArgs([0,30], [10,20])).toStrictEqual(true)
    })
    test('test minimumFillArgs empty segment', () => {
	//nothing needed 
	expect(minimumFillArgs([0,0], [0,20])).toStrictEqual({'start':0, 'end':20})
	expect(minimumFillArgs([0,0], [10,20])).toStrictEqual({'start':10, 'end':20})
    })
})

//export const segE:Segment = [12, 15]
export const segA:Segment = [0,5];
export const dataA:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}];

export const segB:Segment = [2, 7]
export const dataB:DFData = [{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6}];

export const segBShort:Segment = [2, 6]
export const dataBShort:DFData = [{'a':2},{'a':3},{'a':4}, {'a':5}];


export const segC:Segment = [0,7]
export const dataC:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6}];

export const segD:Segment = [8, 11]
export const dataD:DFData = [{'a':8}, {'a':9}, {'a':10} ]


export const segE:Segment = [12, 15]
export const dataE:DFData = [{'a':12}, {'a':13}, {'a':14}]


export const segBD:Segment = [5, 9]
export const dataBD:DFData = [{'a':5}, {'a':6}, {'a':7}, {'a':8}]

export const segBE:Segment = [5, 13]
export const dataBE:DFData = [{'a':5}, {'a':6}, {'a':7}, {'a':8},
			      {'a':9}, {'a':10}, {'a':11}, {'a':12}]



export const segAOffset:Segment = [4, 9];
export const segBOffset:Segment = [6, 11]
export const segCOffset:Segment = [4, 11]

export const fullData09:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6},
				  {'a':7}, {'a':8}]


export const fullData015:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6},
				   {'a':7}, {'a':8},
				   {'a':9}, {'a':10}, {'a':11}, {'a':12}, {'a':13}, {'a':14}]

describe('merge', () => {


    test('test complete overlap', () => {

	expect(merge([segBShort, dataBShort], [segC, dataC])).toStrictEqual(
	    [segC, dataC])
    })

    test('test simple merge', () => {
	expect(merge([segA, dataA] as SegData, [segB, dataB])).toStrictEqual([segC,dataC])

	expect(merge([segA, dataA] as SegData, [segBD, dataBD])).toStrictEqual([[0,9], fullData09]);
    });

    test('test offset simple merge', () => {
	// run the same test as simple merge, with +4 on all offsets, makes sure we aren't special casing 0
	expect(merge([segAOffset, dataA] as SegData, [segBOffset, dataB])).toStrictEqual([segCOffset,dataC])
    });

    test('test different length merge', () => {
	const segBShort:Segment = [3, 7]
	const dataBShort:DFData = [{'a':3},{'a':4}, {'a':5}, {'a':6}];

	expect(merge([segA, dataA] as SegData, [segBShort, dataBShort])).toStrictEqual([segC,dataC])
    });


    test('test mid merge', () => {
	const segEnd:Segment = [5, 7]
	const dataEnd:DFData = [{'a':5}, {'a':6}];
	expect(merge([segA, dataA] as SegData, [segEnd, dataEnd])).toStrictEqual([segC,dataC])
    });
})

describe('mergeSegments', () => {

    test('test merge overlap', () => {
	expect(mergeSegments([segBShort], [dataBShort], segC, dataC)).toStrictEqual(
	    [[segC], [dataC]])
    });

    test('test merge overlap', () => {
	// test overlaps from both sides,  in every case segC is the expected result
	// also test cases where one segment completely overlaps other data

	expect(mergeSegments([segA], [dataA], segC, dataC)).toStrictEqual(
	    [[segC], [dataC]])

	expect(mergeSegments([segC], [dataC], segA, dataA)).toStrictEqual(
	    [[segC], [dataC]])

	expect(mergeSegments([segB], [dataB], segC, dataC)).toStrictEqual(
	    [[segC], [dataC]])

	expect(mergeSegments([segC], [dataC], segB, dataB)).toStrictEqual(
	    [[segC], [dataC]])

	expect(mergeSegments([segBShort], [dataBShort], segC, dataC)).toStrictEqual(
	    [[segC], [dataC]])

	expect(mergeSegments([segC], [dataC], segBShort, dataBShort)).toStrictEqual(
	    [[segC], [dataC]])
    });

    test('test mid merge recursive', () => {
	expect(mergeSegments([segA, segD, segE], [dataA, dataD, dataE], segBE, dataBE)).toStrictEqual(
	    [[[0,15]], [fullData015]])
    });


    test('test merge adjacent', () => {
	expect(mergeSegments([segA], [dataA], segBD, dataBD)).toStrictEqual(
	    [[[0,9]], [fullData09]])
    });

    test('test merge adjacent2', () => {
	expect(mergeSegments([segBD], [dataBD], segA, dataA)).toStrictEqual(
	    [[[0,9]], [fullData09]])
    });


    test('test mid merge', () => {
	const fullData:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6},
				 {'a':7}, {'a':8}, {'a':9}, {'a':10} ];

	expect(mergeSegments([segA, segD], [dataA, dataD], segBD, dataBD)).toStrictEqual(
	    [[[0,11]], [fullData]])
    });

    test('test empty mergeSegments', () => {
	expect(mergeSegments([], [], segA, dataA)).toStrictEqual([[segA],[dataA]])
    });
    test('test simple mergeSegments', () => {
	expect(mergeSegments([segA], [dataA], segB, dataB)).toStrictEqual([[segC],[dataC]])
	expect(mergeSegments([segB], [dataB], segA, dataA)).toStrictEqual([[segC],[dataC]])
	expect(mergeSegments([segA], [dataA], segBD, dataBD)).toStrictEqual([
	    [[0,9]],

	    [fullData09]]);
    });

    test('test mid no merge ', () => {
	expect(mergeSegments([segA], [dataA], segBOffset, dataB)).toStrictEqual([[segA, segBOffset],[dataA, dataB]])
    });

});
describe('range tests', () => {
    test('test getSliceRange', () => {

	expect(getSliceRange(segA, dataA, segA)).toStrictEqual(dataA);
	expect(getSliceRange(segA, dataA, [2,4])).toStrictEqual([{'a':2},{'a':3}])

	expect(getSliceRange(segAOffset, dataA, segAOffset)).toStrictEqual(dataA);
	expect(getSliceRange(segAOffset, dataA, [6,8])).toStrictEqual([{'a':2},{'a':3}])


    })
    test('test getRange', () => {
	expect(getRange([segA, segD], [dataA, dataD], segA)).toStrictEqual(dataA);
	expect(getRange([segA, segD], [dataA, dataD], [2,4])).toStrictEqual([{'a':2},{'a':3}])

	expect(getRange([segAOffset, segE], [dataA, dataE], segAOffset)).toStrictEqual(dataA);
	expect(getRange([segAOffset, segE], [dataA, dataE], [6,8])).toStrictEqual([{'a':2},{'a':3}])

	expect(getRange([segAOffset, segE], [dataA, dataE], segE)).toStrictEqual(dataE);
	expect(getRange([segAOffset, segE], [dataA, dataE], [13, 15])).toStrictEqual([{'a':13},{'a':14}])

    })
})

describe('size management tests', () => {
    test('test segmentsSize', () => {

	expect(segmentsSize([[0,5], [12,15]])).toBe(8)
    })

    test('test compactSegments', () => {
	const keepRange:Segment = [segAOffset[0], segE[0]+1];
	const newSegE:Segment = [segE[0], segE[0]+1];

	expect(compactSegments([segAOffset, segE], [dataA, dataE], keepRange)).toStrictEqual(
	    [[segAOffset, newSegE], [dataA, [dataE[0]]]])
    })

    test('test compactSegments2', () => {

	//using segAOffset because I want to make sure nothing is 0 indexed
	const segAOffset:Segment = [4, 9];
	const dataA:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}];
	const segE:Segment = [12, 15]
	const dataE:DFData = [{'a':12}, {'a':13}, {'a':14}]


	const keepRange:Segment = [5, 13]
	const prevSegments = [segAOffset, segE]
	const expectedSegments = [[5,9], [12,13]]

	const expectedDFs = [[{'a':1},{'a':2},{'a':3},{'a':4}],
			     [{'a':12}]];

	const [actualSegments, actualData] = compactSegments(prevSegments, [dataA, dataE], keepRange)
	expect(actualSegments).toStrictEqual(expectedSegments)
	expect(actualData).toStrictEqual(expectedDFs)
    })
    test('test compactSegments3', () => {
	//same as 2, but with another untouched segment in the middle

	//using segAOffset because I want to make sure nothing is 0 indexed
	const segAOffset:Segment = [4, 7];
	const dataA:DFData = [{'a':0},{'a':1},{'a':2}];
	const segE:Segment = [12, 15]
	const dataE:DFData = [{'a':12}, {'a':13}, {'a':14}]


	const keepRange:Segment = [5, 13]
	const untouchedSegment:Segment = [9,10];
	const prevSegments = [segAOffset, untouchedSegment,  segE]
	const expectedSegments = [[5,7], untouchedSegment, [12,13]]


	const untouchedData:DFData = [{'a':9}];
	const expectedDFs = [[{'a':1},{'a':2}],
			     untouchedData,
			     [{'a':12}]];

	const [actualSegments, actualData] = compactSegments(prevSegments, [dataA, untouchedData, dataE], keepRange)
	expect(actualSegments).toStrictEqual(expectedSegments)
	expect(actualData).toStrictEqual(expectedDFs)
    })
})


const genRows = (low:number, high:number, key:string ='a'):[Segment, DFData] => {
    const retDF = [];
    for(var i=low; i<high; i++) {
	const row:DFDataRow = {};
	row[key] = i
	retDF.push(row)
    }
    return [[low, high] as Segment, retDF]
}

describe('SmartRowCache tests', () => {
    test('basic SmartRowCache tests', () => {

	const src = new SmartRowCache()
	src.maxSize = 35
	src.trimFactor = .8
	expect(src.hasRows([10,20])).toStrictEqual({"start": 10, "end": 20})

	src.addRows.apply(src, genRows(10,20))
	expect(src.hasRows([10,20])).toBe(true)

	src.addRows.apply(src, genRows(20,30))  //make sure the cache is compacted
	expect(src.hasRows([10,30])).toBe(true)

	expect(src.getRows([10, 30])).toStrictEqual(genRows(10,30)[1])
	expect(src.usedSize()).toBe(20)

	src.addRows.apply(src, genRows(35, 45))
	expect(src.usedSize()).toBe(30)
	src.getRows([35,45]) // move the last request up towards the growing end
	src.addRows.apply(src, genRows(45, 55))
	expect(src.usedSize()).toBe(27)  // .8 * 35 = 28, (trimFactor * maxSize) floor


	// we want to verify that the cache was trimmed, and that
	// there is more of the dataframe around the most recently
	// requested side
	expect(src.getExtents()).toStrictEqual([23,55])  
	expect(src.hasRows([0,30])).toStrictEqual({"start": 0, "end": 23})
	
    })

    test('basic SmartRowCache tests2', () => {

	const src = new SmartRowCache()
	src.maxSize = 35

	src.addRows.apply(src, genRows(10,30))  //make sure the cache is compacted
	expect(src.hasRows([10,30])).toBe(true)
	src.addRows.apply(src, genRows(35, 45))
	expect(src.usedSize()).toBe(30)
	src.getRows([35,45]) // move the last request up towards the growing end
	src.addRows.apply(src, genRows(45, 55))
	expect(src.usedSize()).toBe(27)  // .8 * 35 = 28, (trimFactor * maxSize) floor


	// we want to verify that the cache was trimmed, and that
	// there is more of the dataframe around the most recently
	// requested side
	expect(src.getExtents()).toStrictEqual([23,55])
	src.hasRows([0,15])

	// This is an example of a call to addRows that immediately
	// gets trimmed, we should probably throw an error here
	src.addRows.apply(src, genRows(0,30))  
	expect(src.getExtents()).toStrictEqual([0,26])

	expect(src.hasRows([0,30])).toStrictEqual({"start": 26, "end": 30})
	
    })


    test('basic SmartRowCache verify hasRows return True when full dataset size known and less than request', () => {

	const src = new SmartRowCache()
	src.maxSize = 35

	src.addRows.apply(src, genRows(0, 25));
	src.sentLength = 25;
				       
	expect(src.hasRows([0,25])).toBe(true)

	// this should be true because even though we don't have up to 30, the dataset is only 25 long
	expect(src.hasRows([0,30])).toBe(true)
    })

    test('SmartRowCache oppositeTrim side ', () => {

	const src = new SmartRowCache()
	src.maxSize = 35
	expect(src.hasRows([10,20])).toStrictEqual({"start": 10, "end": 20})


	src.addRows.apply(src, genRows(10,20))
	expect(src.hasRows([10,20])).toBe(true)

	src.addRows.apply(src, genRows(20,30))  //make sure the cache is compacted
	expect(src.hasRows([10,30])).toBe(true)

	expect(src.getRows([10, 30])).toStrictEqual(genRows(10,30)[1])
	expect(src.usedSize()).toBe(20)

	src.addRows.apply(src, genRows(35, 45))
	expect(src.usedSize()).toBe(30)
	src.getRows([10, 20]) // move the last request up towards the growing end
	src.addRows.apply(src, genRows(45, 55))
	expect(src.usedSize()).toBe(28)  // .8 * 35 = 28, (trimFactor * maxSize) floor
	expect(src.getExtents()).toStrictEqual([10,43])  
	
    })
})
describe('failing SmartRowCache tests', () => {
      test('SmartRowCache trim premptive request ', () => {
	  // based on patterns seen when actually run
	  const src = new SmartRowCache()
	  src.maxSize = 1000;
	  src.addRows.apply(src, genRows(0,902))

	  // important because we want the most recent hasRows
	  expect(src.hasRows([880,902])).toBe(true)
	  expect(src.hasRows([902, 1002])).toStrictEqual({'start':902, 'end':1002})
	  src.addRows.apply(src, genRows(902,1002))  //force a compaction
	  expect(src.getExtents()).toStrictEqual([223, 1002])
	  expect(src.hasRows([902,924])).toBe(true)
    })
})  

describe('KeyAwareSmartRowCache tests', () => {

    const failNOP = () => {}

    test('basic KeyAwareSmartRowCache tests', () => {
	let src:KeyAwareSmartRowCache;

	const mockRequestFn = jest.fn((_pa:PayloadArgs) => {
	    //console.log("reqFn", pa)
	})

	src = new KeyAwareSmartRowCache(mockRequestFn);

	const pa1: PayloadArgs = {
	    sourceName:"foo", start:0, end:20, origEnd:20}

	const mockCbFn = jest.fn((_df:DFData, _length:number) => {
	    //console.log("mockCbFn", df.length,  length )
	})

	src.getRequestRows(pa1, mockCbFn, failNOP)

	const expectedRequest:PayloadArgs = {...pa1 } ;

	expect(mockRequestFn.mock.calls[0][0]).toStrictEqual(expectedRequest)
    })


    test('test that callback is called', () => {
	let src:KeyAwareSmartRowCache;
	const mockRequestFn = jest.fn((pa:PayloadArgs) => {
	    //console.log("reqFn", pa)
	    const resp:PayloadResponse = {
		key:pa,
		data:genRows(pa.start, pa.end, pa.sourceName)[1],
		length:800
	    }
	    src.addPayloadResponse(resp)
	})

	src = new KeyAwareSmartRowCache(mockRequestFn);

	const pa1: PayloadArgs = {
	    sourceName:"foo", start:0, end:20, origEnd:20}

	const mockCbFn = jest.fn((_df:DFData, _length:number) => {
	    //console.log("mockCbFn", df.length,  length )
	})
	src.getRequestRows(pa1, mockCbFn, failNOP)
	expect(mockCbFn.mock.calls).toHaveLength(1);
    })

    test('KeyAwareSmartRowCache test short data', () => {
	// verify that KeyAwareSmartRowCache handles the case where
	// the returned data is smaller than request size
	let src:KeyAwareSmartRowCache;
	const mockRequestFn = jest.fn((pa:PayloadArgs) => {
	    // we're going to get a request for 20 rows, only send back 17
	    const resp:PayloadResponse = {
		key:pa,
		data:genRows(pa.start, 17, pa.sourceName)[1],
		length:17
	    }
	    src.addPayloadResponse(resp)
	})

	src = new KeyAwareSmartRowCache(mockRequestFn);

	const pa1: PayloadArgs = {
	    sourceName:"foo", start:0, end:20, origEnd:20}

	const mockCbFn = jest.fn((_df:DFData, _length:number) => {})

	src.getRequestRows(pa1, mockCbFn, failNOP)
	expect(mockCbFn.mock.calls).toHaveLength(1);
	const [respData, sentLength] = mockCbFn.mock.calls[0];
	expect(respData.length).toStrictEqual(17)
	expect(sentLength).toStrictEqual(17)
	const pa2: PayloadArgs = {
	    sourceName:"foo", start:0, end:17, origEnd:17}

	const mockCbFn2 = jest.fn((_df:DFData, _length:number) => {})
	src.getRequestRows(pa2, mockCbFn2, failNOP)
	const [respData2, sentLength2] = mockCbFn2.mock.calls[0];
	expect(respData2.length).toStrictEqual(17)
	expect(sentLength2).toStrictEqual(17)
    })

    test('KeyAwareSmartRowCache test last rows', () => {
	// verify that a request that overlaps the end of the data is handled proeprly
	let src:KeyAwareSmartRowCache;
	const mockRequestFn = jest.fn((pa:PayloadArgs) => {
	    if (pa.end > 800) {
		const resp2:PayloadResponse = {
		    key:pa,
		    data:genRows(pa.start, 800, pa.sourceName)[1],
		    length:800
		}
		src.addPayloadResponse(resp2)
		return 
	    }
	    const resp:PayloadResponse = {
		key:pa,
		data:genRows(pa.start, pa.end, pa.sourceName)[1],
		length:800
	    }
	    src.addPayloadResponse(resp)
	})

	src = new KeyAwareSmartRowCache(mockRequestFn);

	const pa1: PayloadArgs = {
	    sourceName:"foo", start:0, end:20, origEnd:20}

	const mockCbFn = jest.fn((df:DFData, _length:number) => {
	    console.log("mockCbFn", df.length,  length )
	})

	src.getRequestRows(pa1, mockCbFn, failNOP)
	expect(mockCbFn.mock.calls).toHaveLength(1);



	const pa2: PayloadArgs = {
	    sourceName:"foo", start:770, end:820, origEnd:820}

	const mockCbFn2 = jest.fn((_df:DFData, _length:number) => {})

	src.getRequestRows(pa2, mockCbFn2, failNOP)
	const [respData2, sentLength2] = mockCbFn2.mock.calls[0];
	expect(respData2.length).toStrictEqual(30)
	expect(sentLength2).toStrictEqual(800)
    })

        test('test trim functionality', () => {
	//these tests aren't perfect, basically I'm trying to verify that trim got called at all.  But it depends heavily on internal settings inside of KeyAwareSmartRowCache and SmartRowCache, because it is checking for exact numbers of rows returned.

	    let src:KeyAwareSmartRowCache;
	    const mockRequestFn = jest.fn((pa:PayloadArgs) => {
		const L = 7700
		if (pa.end > L) {
		    const resp2:PayloadResponse = {
			key:pa,
			data:genRows(pa.start, L, pa.sourceName)[1],
			length:L
		    }
		    src.addPayloadResponse(resp2)
		    return 
		}
		const resp:PayloadResponse = {
		    key:pa,
		    data:genRows(pa.start, pa.end, pa.sourceName)[1],
		    length:L
		}
		src.addPayloadResponse(resp)
	    })

	    src = new KeyAwareSmartRowCache(mockRequestFn);
	    src.maxSize = 3000;

	    const pa1: PayloadArgs = {
		sourceName:"foo", start:0, end:20, origEnd:20}

	    const mockCbFn = jest.fn((_df:DFData, _length:number) => {})
	    src.getRequestRows(pa1, mockCbFn, failNOP)
	    expect(src.usedSize()).toStrictEqual(20);


	    const pa2: PayloadArgs = {
		sourceName:"bar", start:0, end:22, origEnd:22}
	    src.getRequestRows(pa2, mockCbFn, failNOP)
	    expect(src.usedSize()).toStrictEqual(42);

	    const pa3: PayloadArgs = {
		sourceName:"baz", start:0, end:3003, origEnd:3003}
	    src.getRequestRows(pa3, mockCbFn, failNOP)
	    expect(src.usedSize()).toStrictEqual(3045);
	    src.trim();
	    expect(src.usedSize()).toStrictEqual(3025);
	    const pa4: PayloadArgs = {
		sourceName:"qqqq", start:0, end:55, origEnd:55}
	    src.getRequestRows(pa4, mockCbFn, failNOP)
	    expect(src.usedSize()).toStrictEqual(3058);


    })
    
});
