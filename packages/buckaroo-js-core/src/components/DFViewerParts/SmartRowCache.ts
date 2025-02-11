import {
    DFData,
} from "./DFWhole";


export interface RowRequest {
    start:number;
    end:number
}


export type Segment = [number, number];
export type RequestArgs = RowRequest | true;
export type SegData = [Segment, DFData];

export const mergeSegments = (segments:Segment[], dfs:DFData[], newSegment:Segment, newDF:DFData): [Segment[], DFData[]] => {


    if (segments.length == 0) {
	return [[newSegment], [newDF]]
    }
    const [newStart, newEnd] = newSegment;
    const [firstStart, _firstEnd] = segments[0];
    if (newEnd < firstStart) {
	return [[newSegment, ...segments], [newDF, ...dfs]]
    }

    const [retSegments, retDFs]:[Segment[], DFData[]] = [[],[]];

    for(var i=0; i < segments.length; i++) {
	const [seg, df] = [segments[i], dfs[i]];
	if (segmentsOverlap(seg, newSegment)) {
	    const [addSegment, addDf] = merge([seg,df], [newSegment, newDF]);
	    //slicing greater than the length of an array returns []
	    const restSegments = retSegments.concat(segments.slice(i+1))
	    const restDfs = retDFs.concat(dfs.slice(i+1))
	    return mergeSegments(restSegments, restDfs, addSegment, addDf);
	}
	retSegments.push(seg)
	retDFs.push(df)

	if (i < (segments.length -1)) {
	    if (segmentBetween(newSegment, seg, segments[i+1])){
		retSegments.push(newSegment);
		retDFs.push(newDF);
	    }
	}
    }
    const [_lastStart, lastEnd] = segments[segments.length -1];
    if (lastEnd < newStart) {
	retSegments.push(newSegment);
	retDFs.push(newDF);
    }
    return [retSegments, retDFs]
}

export const merge = (leftSD:SegData, rightSD:SegData): SegData => {
    const [leftSeg, leftDF] = leftSD;
    const [rightSeg, rightDF ] = rightSD;
    if (segmentLT(rightSeg, leftSeg)) {
	// it's easier if left is always less than right
	return merge(rightSD, leftSD); 
    }
    const [lStart, lEnd] = leftSeg;
    const [rStart, rEnd] = rightSeg;
    if (lStart < rStart && rEnd < lEnd ){
	// if leftSD entirely contains rightSD, just return left
	return leftSD
    }

    if (lEnd === rStart) {
	const combinedDFData = leftDF.concat(rightDF)
	return [[lStart, rEnd], combinedDFData]
    }
    const sliceEnd = rStart - lEnd;
    const combinedDFData = leftDF.slice(0,sliceEnd).concat(rightDF)
    return [[lStart, rEnd], combinedDFData]
}

export const segmentBetween = (test:Segment, segLow:Segment, segHigh:Segment):boolean => {
    if (segmentLT(segHigh, segLow)) {
	return segmentBetween(test, segHigh, segLow)
    }

    
    const [tStart, tEnd] = test;
    const lowEnd = segLow[1]
    const highStart = segHigh[0];
    if(lowEnd < tStart && tEnd < highStart) {
	return true
    }
    return false;
}

export const segmentLT = (a:Segment, b:Segment):boolean => {
    
    const [aStart, aEnd] = a;
    const [bStart, bEnd] = b;

    if (aStart < bStart) {
	return true
    } else if (aStart == bStart && aEnd < bEnd) {
	//if they start in the same place, but a ends before b
	return true
    }
    return false;
}
    

export const segmentSubset = (outer:Segment, inner:Segment):boolean => {
    
    const [oStart, oEnd] = outer;
    const [iStart, iEnd] = inner;

    if (oStart <= iStart && iEnd <= oEnd) {
	return true }
    return false;
}
    

export const segmentsOverlap = (segmentA:Segment, segmentB:Segment):boolean => {
    if (segmentLT(segmentB, segmentA)) {
	return segmentsOverlap(segmentB, segmentA)
    }
    const [aLow, aHigh] = segmentA;
    const [bLow, bHigh] = segmentB;


    if(aLow <= bHigh && aHigh >= bLow) {
	return true
    }
    return false;
}

export const segmentIntersect = (segmentA:Segment, segmentB:Segment):Segment => {
    const [aLow, aHigh] = segmentA;
    const [bLow, bHigh] = segmentB;
    return [Math.max(aLow, bLow), Math.min(aHigh, bHigh)]
}

export const minimumFillArgs = ( haveSegment:Segment, needSegment:Segment):RequestArgs  => {
    /* given a segment that we have in cache, and a segment we need,
       return the minimum request size to satisfy needSegment */
    const [haveLow, haveHigh] = haveSegment;
    const [needLow, needHigh] = needSegment;

    if (!segmentsOverlap(haveSegment, needSegment)) {
	return {start:needLow, end:needHigh}
    } else if (needLow > haveLow && needHigh < haveHigh) {
	return true
    } 
    // else if (segmentSubset(needSegment, haveSegment)) {
    // 	// this will duplicate the haveSegment, but we can't issue two
    // 	// requests from here rare case not currently encountered by
    // 	// the code, and not worth the complexity
    // 	return {start:needLow, end:needHigh}
    // }
    else if (needLow < haveLow) {
	return {start:needLow, end:haveLow}
    } else if (haveLow < needLow) {
	return {start:haveHigh, end:needHigh}
    }

    return {start:needLow, end:needHigh}
}

export const getSliceRange = (haveSegment:Segment, haveDF:DFData, requestSeg:Segment): DFData => {
    const [hStart, _hEnd] = haveSegment;
    const [rStart, rEnd] = requestSeg;

    const sStart = rStart - hStart;
    const sEnd = rEnd - hStart;
    return haveDF.slice(sStart, sEnd);
}

export const getRange = (segments:Segment[], dfs:DFData[], requestSeg:Segment): DFData => {
    for(var i=0; i < segments.length; i++) {
	const [seg, df] = [segments[i], dfs[i]];
	if(segmentSubset(seg, requestSeg)) {
	    return getSliceRange(seg, df, requestSeg);
	}
    }
    throw new Error(`RequestSeg {requestSeg} not in {segments}`)
}

export const segmentsSize = (segments:Segment[]): number => {
    var accum = 0;
    for(var i=0; i < segments.length; i++) {
	const [start, end] = segments[i];
	accum+= end-start
    }
    return accum;
}


export const slicedSegmentSize = (segments:Segment[], slice:Segment): number => {
    var accum = 0;
    for(var i=0; i < segments.length; i++) {
	if (segmentsOverlap(segments[i], slice)) {
	    const [start, end] = segmentIntersect(segments[i], slice)
	    accum+= end-start
	}
    }
    return accum;
}

export const segmentFromMidOffset = (midPoint:number, offset:number): Segment => {
    return [Math.floor(midPoint - offset), Math.floor(midPoint + offset)] as Segment;
}

export const sizeSlice = (midPoint:number, offset:number, segments:Segment[]): number => {
    return slicedSegmentSize(segments, segmentFromMidOffset(midPoint, offset))
}



export const compactSegments = (segments:Segment[], dfs:DFData[], keep:Segment): [Segment[], DFData[]] => {
    const [retSegments, retDFs]:[Segment[], DFData[]] = [[],[]];

    for(var i=0; i < segments.length; i++) {
	const [seg, df] = [segments[i], dfs[i]];
	if(segmentSubset(keep, seg)) {
	    //if this segment is entirely inside of keep, just add it to retVars
	    retSegments.push(seg)
	    retDFs.push(df)
	} else if (segmentsOverlap(keep, seg)) {
	    // here we have to do something interesting
	    if(segmentLT(keep, seg)) {
		//keepEnd must be less than seg end
		const newSeg:Segment = [seg[0], keep[1]]
		const sliceDf = getSliceRange(seg, df, newSeg)
		retSegments.push(newSeg)
		retDFs.push(sliceDf)
	    } else {
		//the keep window extends beyond the end of this segment,  use the end of seg
		const newSeg:Segment = [keep[0], seg[1]]
		const sliceDf = getSliceRange(seg, df, newSeg)
		retSegments.push(newSeg)
		retDFs.push(sliceDf)
	    }
	}
    }
    return [retSegments, retDFs];
}



export class SmartRowCache {

    public segments: Segment[] = []
    private dfs: DFData[] = []
    // These tuning factors are sensitive.
    // there are other serverside and ag-grid tuning factors too.
    // those are "rowRequestSize" from ag-grid verify prop name
    // and the serverside followon payload size.
    // to be safe  maxSize should be 10* rowRequestSize
    // and followon payload size should be  1/3rd to 1/4 of maxSize

    // RRS = 40
    // maxSize = 400
    // followon = 100

    // given all of this we want some signal for "not at the end of cache, but fire off the next request anyways"

    // the idea is that the user shouldn't have to wait for a server side request.

    // also especially for sorting, that is expensive, fire off the
    // first cache filling with the min, but while that DF is still
    // sorted serverside, sned the followno request.
    
    
    public maxSize: number = 1000;
    public trimFactor:number = 0.8;  // trim down to trimFactor from maxSize
    public lastRequest: Segment = [0,0];

    public usedSize(): number {
	return segmentsSize(this.segments);
    }

    public trimCache(): void {
	if (this.usedSize() < this.maxSize) {
	    return
	}
	if (this.lastRequest[0] == 0 && this.lastRequest[1] == 0) {
	    throw new Error("trying to trim with no requests, unexpected");
	}
	const last = this.lastRequest;

	const lastSegSize = last[1] - last[0]
	const mid = (lastSegSize/2) + last[0];

	var filled = 0;
	
	var targetWindow = Math.floor(this.maxSize * this.trimFactor / 2)
	filled = sizeSlice(mid, targetWindow, this.segments);
	while (filled < this.maxSize) {
	    filled = sizeSlice(mid, targetWindow, this.segments);
	    targetWindow *=2
	}
	
	while (filled > Math.floor(this.maxSize * this.trimFactor)) {
	    targetWindow = Math.floor(.9 * targetWindow)
	    filled = sizeSlice(mid, targetWindow, this.segments);
	}
	       
	const keepSeg = segmentFromMidOffset(mid, targetWindow);
	[this.segments, this.dfs] = compactSegments(this.segments, this.dfs, keepSeg);
    }

    public getExtents():Segment {
	if (this.segments.length === 0) {
	    throw new Error("No Segments");
	}
	const last = this.segments[this.segments.length -1];
	const first = this.segments[0];
	return [first[0], last[1]]
    }
    
    public addRows(newSegment:Segment, newDf:DFData): void {
	const [newSegs, newDfs] = mergeSegments(this.segments, this.dfs, newSegment, newDf)
	this.segments = newSegs;
	this.dfs = newDfs;

	this.trimCache()
    }

    public hasRows(needSeg:Segment): RequestArgs {
	this.lastRequest = needSeg;
	for (const ourSeg of this.segments) {
	    if(segmentSubset(ourSeg, needSeg)) {
		//we have the entire segment
		return true;
	    }
	    if(segmentsOverlap(ourSeg, needSeg)) {
		console.log("ourSeg", ourSeg);
		return minimumFillArgs(ourSeg, needSeg)
	    }
	}
	return minimumFillArgs([0,0], needSeg)
    }

    public getRows(range:Segment): DFData {
	if(this.hasRows(range) === true) {
	    this.lastRequest = range;
	    return getRange(this.segments, this.dfs, range)
	}
	throw new Error(`Missing rows for {range}`)
    }
}
