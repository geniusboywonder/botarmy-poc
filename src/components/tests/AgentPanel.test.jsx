import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AgentPanel from '../AgentPanel';
import { AppContext } from '../../context/AppContext.jsx';

describe('AgentPanel', () => {
  it('renders loading state', () => {
    const contextValue = {
      agents: [],
      loading: { agents: true },
      error: { agents: null },
      refetch: () => {},
    };
    render(
      <AppContext.Provider value={contextValue}>
        <AgentPanel />
      </AppContext.Provider>
    );
    expect(screen.getByText('Loading agents...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    const contextValue = {
      agents: [],
      loading: { agents: false },
      error: { agents: 'Failed to load agents' },
      refetch: () => {},
    };
    render(
      <AppContext.Provider value={contextValue}>
        <AgentPanel />
      </AppContext.Provider>
    );
    expect(screen.getByText('Failed to load agents')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
  });

  it('renders data', () => {
    const contextValue = {
      agents: [{ id: 1, role: 'Tester', status: 'idle' }],
      loading: { agents: false },
      error: { agents: null },
      refetch: () => {},
    };
    render(
      <AppContext.Provider value={contextValue}>
        <AgentPanel />
      </AppContext.Provider>
    );
    expect(screen.getByText('Tester')).toBeInTheDocument();
    expect(screen.getByText('Status: idle')).toBeInTheDocument();
  });
});
