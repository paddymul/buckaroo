import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { OperationsList2 } from './OperationsList';
import { symDf } from './CommandUtils';
import { Operation } from './OperationUtils';

type Meta = Record<string, any>;
const makeOp = (symbol: string, arg: string, meta: Meta = {}): Operation => [
  { symbol, meta },
  symDf,
  arg
];

describe('OperationsList2', () => {
  const operations: Operation[] = [
    makeOp('fillna', 'col1', { auto_clean: true, clean_strategy: 'light-int' }),
    makeOp('dropcol', 'col2'),
    makeOp('remove_outliers', 'col3', { clean_strategy: 'aggressive' }),
  ];
  let setOperations: jest.Mock, setActiveKey: jest.Mock;

  beforeEach(() => {
    setOperations = jest.fn();
    setActiveKey = jest.fn();
  });

  it('renders all operations', () => {
    throw new Error("Not implemented");
    render(
      <OperationsList2
        operations={operations}
        setOperations={setOperations}
        activeKey={''}
        setActiveKey={setActiveKey}
      />
    );
    expect(screen.getByText('fillna')).toBeInTheDocument();
    expect(screen.getByText('dropcol')).toBeInTheDocument();
    expect(screen.getByText('remove_outliers')).toBeInTheDocument();
  });

  it('displays clean_strategy if present', () => {
    render(
      <OperationsList2
        operations={operations}
        setOperations={setOperations}
        activeKey={''}
        setActiveKey={setActiveKey}
      />
    );
    expect(screen.getByText(/Strategy: light-int/)).toBeInTheDocument();
    expect(screen.getByText(/Strategy: aggressive/)).toBeInTheDocument();
  });

  it('applies auto_clean and active classes', () => {
    render(
      <OperationsList2
        operations={operations}
        setOperations={setOperations}
        activeKey={'fillna0'}
        setActiveKey={setActiveKey}
      />
    );
    const items = screen.getAllByRole('button', { name: /×/ }).map(btn => btn.closest('.operation-item'));
    expect(items[0]).toHaveClass('auto_clean');
    expect(items[0]).toHaveClass('active');
    expect(items[1]).not.toHaveClass('auto_clean');
    expect(items[1]).not.toHaveClass('active');
  });

  it('calls setActiveKey when an item is clicked', () => {
    render(
      <OperationsList2
        operations={operations}
        setOperations={setOperations}
        activeKey={''}
        setActiveKey={setActiveKey}
      />
    );
    const item = screen.getByText('dropcol').closest('.operation-item');
    fireEvent.click(item!);
    expect(setActiveKey).toHaveBeenCalled();
  });

  it('calls setOperations when delete is clicked', () => {
    render(
      <OperationsList2
        operations={operations}
        setOperations={setOperations}
        activeKey={''}
        setActiveKey={setActiveKey}
      />
    );
    const deleteBtn = screen.getAllByRole('button', { name: /×/ })[0];
    fireEvent.click(deleteBtn);
    expect(setOperations).toHaveBeenCalled();
  });

  it('calls setOperations when preserve is clicked', () => {
    render(
      <OperationsList2
        operations={operations}
        setOperations={setOperations}
        activeKey={''}
        setActiveKey={setActiveKey}
      />
    );
    const preserveBtn = screen.getByRole('button', { name: /preserve/ });
    fireEvent.click(preserveBtn);
    expect(setOperations).toHaveBeenCalled();
  });
}); 