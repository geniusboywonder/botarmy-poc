import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Dashboard from '../Dashboard';
import { AppContext } from '../../../context/AppContext.jsx';

// Mock child components
vi.mock('../../AgentPanel', () => ({
    default: () => <div data-testid="agent-panel">Agent Panel</div>
}));
vi.mock('../../ActionQueue', () => ({
    default: () => <div data-testid="action-queue">Action Queue</div>
}));
vi.mock('../../ProjectViewer', () => ({
    default: () => <div data-testid="project-viewer">Project Viewer</div>
}));

describe('Dashboard', () => {
  it('renders its child components', () => {
    const contextValue = {
      agents: [],
      tasks: [],
      artifacts: {},
      loading: { agents: false, tasks: false, artifacts: false },
      error: { agents: null, tasks: null, artifacts: null },
      refetch: () => {},
    };

    render(
      <AppContext.Provider value={contextValue}>
        <Dashboard />
      </AppContext.Provider>
    );

    expect(screen.getByTestId('agent-panel')).toBeInTheDocument();
    expect(screen.getByTestId('action-queue')).toBeInTheDocument();
    expect(screen.getByTestId('project-viewer')).toBeInTheDocument();
  });
});
