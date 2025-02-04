import {
    DFData,
} from "./DFWhole";


export interface RowRequest {
    start:number;
    end:number
}


export type Segment = [number, number];
export type RequestArgs = RowRequest | false;
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

    //if rStart === lEnd we need to do something different
    // probably don't want to slice at all
    const sliceEnd = rStart === lEnd ? leftDF.length : rStart - lEnd;
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

export const minimumFillArgs = ( haveSegment:Segment, needSegment:Segment):RequestArgs  => {
    /* given a segment that we have in cache, and a segment we need,
       return the minimum request size to satisfy needSegment */
    const [haveLow, haveHigh] = haveSegment;
    const [needLow, needHigh] = needSegment;

    if (!segmentsOverlap(haveSegment, needSegment)) {
	return {start:needLow, end:needHigh}
    } else if (needLow > haveLow && needHigh < haveHigh) {
	return false
    } else if (needLow < haveHigh) {
	return {start:haveHigh, end:needHigh}
    } else {
	return {start:needLow, end:haveLow}
    }
    return {start:needLow, end:needHigh}
}



export class SmartRowCache {
    private rowSegments: DFData[] = [[]]
    //private segments: Segment[]
    offsets: Segment[] = [];

    
    public addRows(rows:DFData, start:number, end:number): void {
	for (const [segStart, segEnd] of this.offsets) {
	    console.log(segStart, segEnd, rows, start, end)
	    
	}
	console.log(this.rowSegments);
	// handle accounting with offsets and rowSegments
    }

    public hasRows(start:number, end:number): RequestArgs {
	for (const [segStart, segEnd] of this.offsets) {
	    if(segStart < start) {
		if(segEnd > end) {
		    return false;
		} else {
		    return {start:segEnd, end:end}
		}
	    } else if (segEnd > end) {
	}
	return {start, end}
	}
	return false // doublecheck  
    }
}


/*
export interface IDisplayArgs {
    data_key: string;
    df_viewer_config: DFViewerConfig;
    summary_stats_key: string;
}

export class LruCache<T> {
    private values: Map<string, T> = new Map<string, T>();
    private maxEntries = 10;

    public get(key: string): T | undefined {
        const hasKey = this.values.has(key);
        if (hasKey) {
            // peek the entry, re-insert for LRU strategy
            const maybeEntry = this.values.get(key);
            if (maybeEntry === undefined) {
                throw new Error(`unexpected undefined for ${key}`);
            }
            const entry: T = maybeEntry;
            this.values.delete(key);
            this.values.set(key, entry);
            return entry;
        }
        return undefined;
    }

    public put(key: string, value: T) {
        if (this.values.size >= this.maxEntries) {
            // least-recently used cache eviction strategy
            const keyToDelete = this.values.keys().next().value;
            console.log(`deleting ${keyToDelete}`);
            this.values.delete(String(keyToDelete));
        }

        this.values.set(key, value);
    }
}
export type RespCache = LruCache<PayloadResponse>;



export interface TimedIDatasource extends IDatasource {
    createTime: Date;
}
*/
