import React from "react";

import "./page.css";
import { Operation, OperationDefaultArgs, sym } from "./components/OperationUtils";
import { CommandArgSpec, CommandConfigT, symDf } from "./components/CommandUtils";
import { OperationViewer } from "./components/Operations";




const bakedOperationDefaults: OperationDefaultArgs = {
    dropcol: [sym('dropcol'), symDf, 'col'],
    fillna: [sym('fillna'), symDf, 'col', 8],
    remove_outliers: [sym('remove_outliers'), symDf, 'col', 0.02],
    search: [sym('search'), symDf, 'col', 'term'],
    resample: [sym('resample'), symDf, 'col', 'monthly', {}],
  };

  export const bakedArgSpecs: CommandArgSpec = {
    dropcol: [null],
    fillna: [[3, 'fillVal', 'type', 'integer']],
    remove_outliers: [[3, 'tail', 'type', 'float']],
    search: [[3, 'needle', 'type', 'string']],
    resample: [
      [3, 'frequency', 'enum', ['daily', 'weekly', 'monthly']],
      [4, 'colMap', 'colEnum', ['null', 'sum', 'mean', 'count']],
    ],
  };
 const bakedCommandConfig: CommandConfigT = {
    argspecs: bakedArgSpecs,
    defaultArgs: bakedOperationDefaults,
  };

const bakedOperations: Operation[] = [
    [sym('dropcol'), symDf, 'col1'],
    [sym('fillna'), symDf, 'col2', 5],
    [sym('resample'), symDf, 'month', 'monthly', {}],
  ];
export const Page: React.FC = () => {
     console.log("45")
    return (
        <article>
            <section className="storybook-page">
            <OperationViewer
                operations={bakedOperations}
            setOperations={(foo: unknown) => {
                console.log('setCommands sent', foo);
            }}
            activeColumn={'foo-column'}
            allColumns={['foo-col', 'bar-col', 'baz-col']}
            command_config={bakedCommandConfig}
        />
        </section>
        </article>
        );
    };
