import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { OperationsList } from "../components/OperationsList";
import { Operation, sym } from "../components/OperationUtils";
import { symDf } from "../components/CommandUtils";

const meta = {
    title: "Components/OperationsList",
    component: OperationsList,
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof OperationsList>;

export default meta;
type Story = StoryObj<typeof meta>;

// Sample operations for stories
const sampleOperations: Operation[] = [
    [sym("dropcol"), symDf, "col1"],
    [sym("fillna"), symDf, "col2", 5],
    [sym("resample"), symDf, "month", "monthly", {}],
];

const OperationsListWrapper = ({ operations }: { operations: Operation[] }) => {
    const [ops, setOps] = React.useState<Operation[]>(operations);
    return <OperationsList operations={ops} setOperations={setOps} />;
};

export const Default: Story = {
    args: {
        operations: sampleOperations,
        setOperations: (ops: Operation[]) => console.log("Operations updated:", ops),
    },
    render: (args) => <OperationsListWrapper operations={args.operations} />,
};

export const Empty: Story = {
    args: {
        operations: [],
        setOperations: (ops: Operation[]) => console.log("Operations updated:", ops),
    },
    render: (args) => <OperationsListWrapper operations={args.operations} />,
};

export const SingleOperation: Story = {
    args: {
        operations: [sampleOperations[0]],
        setOperations: (ops: Operation[]) => console.log("Operations updated:", ops),
    },
    render: (args) => <OperationsListWrapper operations={args.operations} />,
};

export const ManyOperations: Story = {
    args: {
        operations: [
            ...sampleOperations,
            [sym("dropcol"), symDf, "col3"],
            [sym("fillna"), symDf, "col4", 10],
            [sym("resample"), symDf, "year", "yearly", {}],
        ],
        setOperations: (ops: Operation[]) => console.log("Operations updated:", ops),
    },
    render: (args) => <OperationsListWrapper operations={args.operations} />,
}; 