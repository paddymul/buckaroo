import {
    DFData,
    DFDataRow
} from "./DFWhole";


export interface RowRequest {
    start:number;
    end:number
}


export type Segment = [number, number];
export type RequestArgs = RowRequest | false;
export type SegData = [Segment, DFData];

const mergeSegments = (segments:Segment[], dfs:DFData[], newSegment:Segment, newDF:DFData): [Segment[], DFData[]] => {


    if (segments.length == 0) {
	return [[newSegment], [newDF]]
    }
    const [newStart, newEnd] = newSegment;
    const [firstStart, firstEnd] = segments[0];
    if (newEnd < firstStart) {
	return [[newSegment, ...segments], [newDF, ...dfs]]
    }

    const [retSegments, retDFs] = [[],[]];

    for(var i=0; i < segments.length; i++) {
	const [seg, df] = [segments[i], dfs[i]];
	if (segmentsOverlap(seg, newSegment)) {
	    const [addSegment, addDf] = merge([seg,df], [newSegment, newDf]);
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
    const [lastStart, lastEnd] = segments[segments.length -1];
    if (lastEnd < newStart) {
	retSegments.push(newSegment);
	retDFs.push(newDF);
    }
    return [retSegments, retDFs]
}

const merge = (leftSD:SegData, rightSD:SegData): SegData => {
    const [leftSeg, leftDF] = leftSD;
    const [rightSeg, rightDF ] = rightSD;
    if (segmentLT(rightSeg, leftSeg)) {
	// it's easier if left is always less than right
	return merge(rightSD, leftSD); 
    }
    const [lStart, lEnd] = leftSeg;
    const [rStart, rEnd] = rightSeg;

    const sliceEnd = rStart - lEnd;
    
    const combinedDFData = leftDF.slice(0,sliceEnd).concat(rightDF)
    return [[lStart, rEnd], combinedDFData]
}

const segmentBetween = (test, segLow, segHigh) {
    const [tStart, tEnd] = test;
    const lowEnd = segLow[1]
    const highStart = segHigh[0];
    if(lowEnd < tStart && highStart < tEnd) {
	return true
    }
    return false;
}

const segmentLT = (a:Segment, b:Segment):boolean => {
    
    const [aStart, _aEnd] = a;
    const [bStart, _bEnd] = b;
    if (aStart < bStart) {
	return true
    }
    return false;
}
    

const segmentsOverlap(segmentA:Segment, segmentB:Segment):boolean {
    const [aLow, aHigh] = segmentA;
    const [bLow, bHigh] = segmentB;

    if(aLow > bLow && aLow < bHigh) {
	return true;
    } else if (aHigh > bLow && aHigh < bHigh) {
	return true;
    }
    return false;
}

const minimumFillArgs( haveSegment:Segment, needSegment:Segment):RowRequest {
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
    private segments: Segment[]

    public addRows(rows, start, end): void {
	for (const [segStart, segEnd] of this.offsets) {
	    
	}
	// handle accounting with offsets and rowSegments
    }

    public hasRows(start, end): RequestArgs {
	for (const [segStart, segEnd] of this.offsets) {
	    if(segStart < start) {
		if(segEnd > end) {
		    return false;
		} else {
		    return {start:segEnd, end:end}
		}
	    } else if 		if(segEnd > end) {
	}
	return {start, end}
    }

}



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
