import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AppContext } from '../../context/AppContext';
import ActionQueue from '../ActionQueue';
import * as api from '../../utils/api';

// Mock the api module
vi.mock('../../utils/api');

const renderWithContext = (ui, { providerProps, ...renderOptions }) => {
  return render(
    <AppContext.Provider value={providerProps}>{ui}</AppContext.Provider>,
    renderOptions
  );
};

describe('ActionQueue', () => {
  const mockTasks = [
    {
      id: 'action1',
      title: 'Approve Deployment',
      description: 'The new version is ready to be deployed to production.',
      priority: 'high',
      options: ['Approve', 'Reject'],
    },
  ];

  it('renders a list of actions', () => {
    const providerProps = {
      tasks: mockTasks,
      loading: { tasks: false },
      error: { tasks: null },
      refetch: vi.fn(),
    };
    renderWithContext(<ActionQueue />, { providerProps });
    expect(screen.getByText('Approve Deployment')).toBeInTheDocument();
    expect(screen.getByText('The new version is ready to be deployed to production.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Approve' })).toBeInTheDocument();
  });

  it('calls respondToAction and refetches when an action button is clicked', async () => {
    const refetch = vi.fn();
    const respondToActionMock = vi.spyOn(api, 'respondToAction').mockResolvedValue({ status: 'ok' });

    const providerProps = {
      tasks: mockTasks,
      loading: { tasks: false },
      error: { tasks: null },
      refetch,
    };
    renderWithContext(<ActionQueue />, { providerProps });

    const approveButton = screen.getByRole('button', { name: 'Approve' });
    fireEvent.click(approveButton);

    // Check that the button is disabled and shows submitting text
    expect(approveButton).toBeDisabled();
    expect(screen.getByText('Submitting...')).toBeInTheDocument();

    await waitFor(() => {
      expect(respondToActionMock).toHaveBeenCalledWith('action1', 'Approve');
    });

    await waitFor(() => {
      expect(refetch).toHaveBeenCalledWith('tasks');
    });
  });

  it('shows an empty state message when there are no tasks', () => {
    const providerProps = {
      tasks: [],
      loading: { tasks: false },
      error: { tasks: null },
      refetch: vi.fn(),
    };
    renderWithContext(<ActionQueue />, { providerProps });
    expect(screen.getByText('No pending actions.')).toBeInTheDocument();
  });
});
