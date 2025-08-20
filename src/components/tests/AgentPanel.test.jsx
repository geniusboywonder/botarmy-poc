import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AppContext } from '../../context/AppContext';
import AgentPanel from '../AgentPanel';

// Mock the AgentCard component to simplify testing
vi.mock('../shared/AgentCard.jsx', () => ({
  default: ({ agent, onToggleExpand }) => (
    <div data-testid={`agent-card-${agent.id}`} onClick={() => onToggleExpand(agent.id)}>
      <p>{agent.role}</p>
      <p>{agent.status}</p>
    </div>
  ),
}));

const renderWithContext = (ui, { providerProps, ...renderOptions }) => {
  return render(
    <AppContext.Provider value={providerProps}>{ui}</AppContext.Provider>,
    renderOptions
  );
};

describe('AgentPanel', () => {
  it('renders loading state', () => {
    const providerProps = {
      agents: [],
      setAgents: vi.fn(),
      loading: { agents: true },
      error: { agents: null },
      refetch: vi.fn(),
    };
    renderWithContext(<AgentPanel />, { providerProps });
    expect(screen.getByText('Loading agents...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    const providerProps = {
      agents: [],
      setAgents: vi.fn(),
      loading: { agents: false },
      error: { agents: 'Failed to load' },
      refetch: vi.fn(),
    };
    renderWithContext(<AgentPanel />, { providerProps });
    expect(screen.getByText('Failed to load')).toBeInTheDocument();
  });

  it('renders a list of agent cards', () => {
    const mockAgents = [
      { id: 'analyst', role: 'Analyst', status: 'working', expanded: false },
      { id: 'architect', role: 'Architect', status: 'idle', expanded: false },
    ];
    const providerProps = {
      agents: mockAgents,
      setAgents: vi.fn(),
      loading: { agents: false },
      error: { agents: null },
      refetch: vi.fn(),
    };
    renderWithContext(<AgentPanel />, { providerProps });
    expect(screen.getByTestId('agent-card-analyst')).toBeInTheDocument();
    expect(screen.getByTestId('agent-card-architect')).toBeInTheDocument();
    expect(screen.getByText('Analyst')).toBeInTheDocument();
  });

  it('calls setAgents when an agent card is clicked to toggle expansion', () => {
    const mockAgents = [{ id: 'analyst', role: 'Analyst', status: 'working', expanded: false }];
    const setAgents = vi.fn();
    const providerProps = {
      agents: mockAgents,
      setAgents,
      loading: { agents: false },
      error: { agents: null },
      refetch: vi.fn(),
    };
    renderWithContext(<AgentPanel />, { providerProps });

    const agentCard = screen.getByTestId('agent-card-analyst');
    fireEvent.click(agentCard);

    expect(setAgents).toHaveBeenCalledTimes(1);
    expect(setAgents).toHaveBeenCalledWith([
      { ...mockAgents[0], expanded: true },
    ]);
  });
});
