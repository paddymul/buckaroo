import React from 'react';
import { getOperationKey, Operation, SetOperationsFunc } from './OperationUtils';

export interface OperationsListProps {
    operations: Operation[];
    setOperations: SetOperationsFunc;
    activeKey:string;
    setActiveKey: React.Dispatch<React.SetStateAction<string>>;
}

export const OperationsList2: React.FC<OperationsListProps> = (
    { operations, setOperations, activeKey, setActiveKey }) => {
    const handleDeleteOperation = (index: number) => {
        const newOperations = [...operations];
        newOperations.splice(index, 1);
        setOperations(newOperations);
    };

    return (
        <div className="operations-list" style={{ 
            display: 'flex', 
            flexDirection: 'row', 
            gap: '8px',
            flexWrap: 'wrap',
            alignItems: 'center'
        }}>
            {operations.map((operation, index) => {
                const currentKey = getOperationKey(operations, index);
                return (<div 
                    key={index} 
                    style={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        gap: '4px',
                        padding: '4px 8px',

                        borderRadius: '4px'
                    }}
                    className={(activeKey===currentKey ? 'active': 'no-class')}
                    onClick={()=> setActiveKey(currentKey)}
                >
                    <span>{operation[0].symbol}</span>
                    <span>{operation[2]}</span>

                    <button
                        onClick={() => handleDeleteOperation(index)}
                        style={{
                            border: 'none',
                            background: 'none',
                            cursor: 'pointer',
                            color: '#ff4444',
                            padding: '2px 4px'
                        }}
                    >
                        ×
                    </button>
                </div>
            )})}
        </div>);
        }
