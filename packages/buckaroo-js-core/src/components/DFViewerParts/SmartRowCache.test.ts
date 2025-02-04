//import { describe, expect } from 'jest';
import {
    Segment,
    segmentLT,
    segmentBetween,
    segmentsOverlap,
    merge,
    SegData
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


const segA:Segment = [0,5];
const dataA:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}];

const segB:Segment = [2, 7]
const dataB:DFData = [{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6}];

const segC:Segment = [0,7]
const dataC:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6}];


const segAOffset:Segment = [3, 8];
const segBOffset:Segment = [5, 10]
const segCOffset:Segment = [3, 10]


describe('merge', () => {
    test('test simple merge', () => {
	expect(merge([segA, dataA] as SegData, [segB, dataB])).toStrictEqual([segC,dataC])
    });

    test('test offset simple merge', () => {
	// run the same test as simple merge, with +3 on all offsets, makes sure we aren't special casing 0
	expect(merge([segAOffset, dataA] as SegData, [segBOffset, dataB])).toStrictEqual([segCOffset,dataC])
    });

    test('test different lengthmerge', () => {
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
