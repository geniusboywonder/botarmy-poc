import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { AppContext } from '../../context/AppContext';
import StatusBar from '../StatusBar';

const renderWithContext = (ui, { providerProps, ...renderOptions }) => {
  return render(
    <AppContext.Provider value={providerProps}>{ui}</AppContext.Provider>,
    renderOptions
  );
};

describe('StatusBar', () => {
  it('renders agent and task counts correctly', () => {
    const providerProps = {
      agents: [{ status: 'idle' }, { status: 'working' }],
      tasks: [{ status: 'WIP' }, { status: 'To Do' }, { status: 'Done' }],
      error: { agents: null, tasks: null },
    };
    renderWithContext(<StatusBar />, { providerProps });

    expect(screen.getByText(/Agents: 1 idle, 1 busy/i)).toBeInTheDocument();
    expect(screen.getByText(/Tasks in Queue: 2/i)).toBeInTheDocument();
  });

  it('renders Connected status when there are no errors', () => {
    const providerProps = {
      agents: [{ status: 'idle' }],
      tasks: [],
      error: { agents: null, tasks: null },
    };
    renderWithContext(<StatusBar />, { providerProps });
    expect(screen.getByText(/Connected/i)).toBeInTheDocument();
  });

  it('renders Error status when there is an error in the context', () => {
    const providerProps = {
      agents: [],
      tasks: [],
      error: { agents: 'Failed to fetch', tasks: null },
    };
    renderWithContext(<StatusBar />, { providerProps });
    expect(screen.getByText(/Error/i)).toBeInTheDocument();
  });
});
