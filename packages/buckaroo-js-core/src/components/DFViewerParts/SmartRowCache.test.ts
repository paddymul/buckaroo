//import { describe, expect } from 'jest';
import {
    Segment,
    segmentLT } from "./SmartRowCache"


describe('foo', () => {
    test('test segmentLT', () => {
	const high:Segment = [50, 100]
	const low:Segment = [20,30]
	expect(segmentLT(low, high)).toBe(true);
	expect(segmentLT(high, low)).toBe(false);
	expect(segmentLT(high, high)).toBe(false);
    });
})
