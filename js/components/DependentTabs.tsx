import React, {
    Component,
    useState,
    useEffect,
    CSSProperties,
    Dispatch,
    SetStateAction
} from 'react';
import {tableDf, DFWhole, EmptyDf} from './staticData';
import {requestDf} from './utils';
import {DFViewer} from './DFViewer';
import _ from 'lodash';
import {Operation} from './OperationUtils';

export function OperationDisplayer({filledOperations, style}) {
    const baseStyle = {margin: '0', textAlign: 'left'};
    const localStyle = {...baseStyle, ...style};
    return (
        <div className='command-displayer' style={{width: '100%'}}>
            <pre style={localStyle}>{JSON.stringify(filledOperations)}</pre>
        </div>
    );
}

export function PythonDisplayer({style, generatedPyCode}) {
    const baseStyle = {margin: '0', textAlign: 'left'};
    const localStyle = {...baseStyle, ...style};
    return (
        <div className='python-displayer' style={{width: '100%'}}>
            <pre style={localStyle}>{generatedPyCode}</pre>
        </div>
    );
}

const makeFullInstructions = (raw) => [{symbol: 'begin'}, ...raw];
const EmptyInstructions = makeFullInstructions([]);
const transformInstructions = (raw) => JSON.stringify(raw);

export const serverGetTransformRequester = (setDf) => {
    const baseRequestTransform = (passedInstructions) => {
        const URLBase = 'http://localhost:5000/dcf/';
        const sliceArgs = 'slice_start=3&slice_end=50';

        const emptyUrl = `${URLBase}df/1?${sliceArgs}`;
        const instructions = transformInstructions(passedInstructions);
        const transUrl = `${URLBase}transform_df/1?instructions=${instructions}&${sliceArgs}`;
        if (_.isEqual(passedInstructions, EmptyInstructions)) {
            requestDf(emptyUrl, setDf);
        } else {
            requestDf(transUrl, setDf);
        }
    };
    return baseRequestTransform;
};

export function TransformViewer({
    style,
    transformedDf
}: {
    style: CSSProperties;
    transformedDf: DFWhole;
}) {
    return (
        <div className='transform-viewer'>
            <DFViewer style={style} df={transformedDf} />
        </div>
    );
}
export type OperationResult = {
    transformed_df: DFWhole;
    generated_py_code: string;
    transform_error?: string;
};

export type OrRequesterT = (ops: Operation[]) => void;
export type getOperationResultSetterT = (
    setter: Dispatch<SetStateAction<OperationResult>>
) => OrRequesterT;

export const baseOperationResults: OperationResult = {
    transformed_df: EmptyDf,
    generated_py_code: 'default py code'
};

export function TabComponent({currentTab, _setTab, tabName}) {
    return (
        <li
            onClick={() => {
                _setTab(tabName);
            }}
            className={currentTab === tabName ? 'active' : ''}
        >
            {tabName}
        </li>
    );
}

export function DependentTabs({
    filledOperations,
    operationResult
}: {
    filledOperations: Operation[];
    operationResult: OperationResult;
}) {
    const [tab, _setTab] = useState('DataFrame');
    const style = {height: '45vh'};
    console.log('dependenttabs operationResult', operationResult);
    return (
        <div className='dependent-tabs' style={{width: '100%'}}>
            <ul className='tabs'>
                <TabComponent currentTab={tab} _setTab={_setTab} tabName={'DataFrame'} />
                <TabComponent currentTab={tab} _setTab={_setTab} tabName={'Python'} />
                <TabComponent currentTab={tab} _setTab={_setTab} tabName={'Operations'} />
            </ul>
            <div className='output-area'>
                {operationResult.transform_error ? (
                    <div>
                        <h2> error </h2>
                        <PythonDisplayer
                            style={style}
                            generatedPyCode={operationResult.transform_error}
                        />
                    </div>
                ) : (
                    <span></span>
                )}
                {
                    {
                        Operations: (
                            <OperationDisplayer style={style} filledOperations={filledOperations} />
                        ),
                        Python: (
                            <PythonDisplayer
                                style={style}
                                generatedPyCode={operationResult.generated_py_code}
                            />
                        ),
                        DataFrame: (
                            <TransformViewer
                                style={style}
                                transformedDf={operationResult.transformed_df}
                            />
                        )
                    }[tab]
                }
            </div>
        </div>
    );
}
