//import { describe, expect } from 'jest';
import {
    Segment,
    segmentLT,
    segmentsOverlap
} from "./SmartRowCache"


const low:Segment = [20,30]
const mid:Segment = [ 25, 55];
const high:Segment = [50, 100]
const around:Segment = [20,120]
describe('foo', () => {
    test('test segmentLT', () => {
	expect(segmentLT(low, high)).toBe(true);
	expect(segmentLT(high, low)).toBe(false);
	expect(segmentLT(high, high)).toBe(false);
	expect(segmentLT(around, high)).toBe(false);
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
