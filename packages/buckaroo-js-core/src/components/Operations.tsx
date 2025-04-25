import React, { useState } from "react";
import _ from "lodash";
import { Operation, SetOperationsFunc, OperationEventFunc } from "./OperationUtils";
import { CommandConfigT } from "./CommandUtils";
import { replaceInArr } from "./utils";

import { OperationDetail } from "./OperationDetail";
import { OperationsList2 } from "./OperationsList";
import { AgGridReact } from "@ag-grid-community/react"; // the AG Grid React Component
import { ColDef, GridOptions } from "@ag-grid-community/core";
//import { CustomCellRendererProps } from '@ag-grid-community/react';

import { updateAtMatch } from "./utils";
import { ModuleRegistry } from "@ag-grid-community/core";
import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";

ModuleRegistry.registerModules([ClientSideRowModelModule]);





export const OperationAdder = ({
    column,
    addOperationCb,
    defaultArgs,
}: {
    column: string;
    addOperationCb: any;
    defaultArgs: any;
}): JSX.Element => {
    const addOperationByName = (localOperationName: string) => {
        return () => {
            const defaultOperation = defaultArgs[localOperationName];
            addOperationCb(replaceInArr(defaultOperation, "col", column));
        };
    };

    return (
        <div className="operation-adder">
            <span className={"column-name"}> Column: {column}</span>
            <fieldset>
                {_.keys(defaultArgs).map((optionVal) => (
                    <button key={optionVal} onClick={addOperationByName(optionVal)}>
                        {" "}
                        {optionVal}{" "}
                    </button>
                ))}
            </fieldset>
        </div>
    );
};

export const OperationViewer = ({
    operations,
    setOperations,
    activeColumn,
    allColumns,
    command_config,
}: {
    operations: Operation[];
    setOperations: SetOperationsFunc;
    activeColumn: string;
    allColumns: string[];
    command_config: CommandConfigT;
}) => {
    const opToKey = (idx: number, op: Operation): string => {
        const name = op[0]["symbol"];
        return name + idx.toString();
    };

    const operationObjs = _.map(Array.from(operations.entries()), ([index, element]) => {
        const rowEl: Record<string, Operation> = {};
        rowEl[opToKey(index, element)] = element;
        return rowEl;
    });
    //why am I doing this? probably something so I gauruntee a clean dict

    const operationDict = _.merge({}, ...operationObjs);

    const idxObjs = _.map(Array.from(operations.entries()), ([index, element]) => {
        const rowEl: Record<string, number> = {};
        rowEl[opToKey(index, element)] = index;
        return rowEl;
    });
    const keyToIdx = _.merge({}, ...idxObjs);

    // previously was null
    const [activeKey, setActiveKey] = useState("");

    function getSetOperation(key: string): OperationEventFunc {
        return (newOperation: Operation) => {
            const index = keyToIdx[key];
            const nextOperations = operations.map((c, i) => {
                if (i === index) {
                    return newOperation;
                } else {
                    return c;
                }
            });
            console.log("about to call setOperations", key, newOperation);
            setOperations(nextOperations);
        };
    }
    const getColumns = (passedOperations: Operation[]): ColDef[] =>
        _.map(Array.from(passedOperations.entries()), ([index, element]) => {
            const name = element[0]["symbol"];
            const key = name + index.toString();
            const column = { field: key, headerName: name }; // width: 20, maxWidth: 60};
            return column;
        });
    const addOperation: OperationEventFunc = (newOperation: Operation) => {
        const newOperationArr = [...operations, newOperation];
        setOperations(newOperationArr);
        const newOperationKey = getColumns(newOperationArr)[newOperationArr.length - 1].field;
        if (newOperationKey !== undefined) {
            setActiveKey(newOperationKey);
        }
    };
    const { argspecs, defaultArgs } = command_config;
    return (
        <div className="operations-viewer">
            <OperationAdder
                column={activeColumn}
                addOperationCb={addOperation}
                defaultArgs={defaultArgs}
            />
            <div className="operations-box">
                <h4> Operations </h4>
                <OperationsList2
                    operations={operations}
                    activeKey={activeKey}
                    setActiveKey={setActiveKey}
                    setOperations={setOperations}
                />
            </div>
            {activeKey && (
                <OperationDetail
                    command={operationDict[activeKey]}
                    setCommand={getSetOperation(activeKey)}
                    columns={allColumns}
                    commandPatterns={argspecs}
                />
            )}
        </div>
    );
};
