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


describe('merge', () => {
    test('test merge', () => {

	const segA:Segment = [0,5];
	const dataA:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}];

	const segB:Segment = [2, 7]
	const dataB:DFData = [{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6}];

	const segC:Segment = [0,7]
	const dataC:DFData = [{'a':0},{'a':1},{'a':2},{'a':3},{'a':4}, {'a':5}, {'a':6}];


	expect(merge([segA, dataA] as SegData, [segB, dataB])).toStrictEqual([segC,dataC])
    });
})
