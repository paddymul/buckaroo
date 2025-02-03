import { describe, it, expect } from 'vitest';
import {
    segmentLT } from "./SmartRowCache"


describe('foo', () => {
    test('test segmentLT', () => {
	const high = [50, 100]
	const low = [20,30]
	expect(segmentLT(low, high)).toBe(true);
	expect(segmentLT(high, low)).toBe(false);
	expect(segmentLT(high, high)).toBe(true);
    });
})
