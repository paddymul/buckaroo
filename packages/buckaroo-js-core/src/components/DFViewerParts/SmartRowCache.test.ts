//import { describe, expect } from 'jest';
import {
    Segment,
    segmentLT,
    segmentBetween,
    segmentsOverlap,
    merge,
    mergeSegments,
    SegData,
} from "./SmartRowCache"
import {
    DFData,
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
    });
})


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
