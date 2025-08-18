import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { AppContext } from '../../context/AppContext';
import ProjectViewer from '../ProjectViewer';

const renderWithContext = (ui, { providerProps, ...renderOptions }) => {
  return render(
    <AppContext.Provider value={providerProps}>{ui}</AppContext.Provider>,
    renderOptions
  );
};

describe('ProjectViewer', () => {
  const mockArtifacts = {
    'src': {
      'components': [
        { name: 'Button.jsx' }
      ],
      'App.jsx': 'file content'
    },
    'package.json': 'file content'
  };

  it('renders the file and folder structure', () => {
    const providerProps = {
      artifacts: mockArtifacts,
      loading: { artifacts: false },
      error: { artifacts: null },
      refetch: () => {},
    };
    renderWithContext(<ProjectViewer />, { providerProps });

    expect(screen.getByTestId('treeitem-src')).toBeInTheDocument();
    expect(screen.getByTestId('treeitem-components')).toBeInTheDocument();
    expect(screen.getByTestId('treeitem-Button.jsx')).toBeInTheDocument();
    expect(screen.getByTestId('treeitem-App.jsx')).toBeInTheDocument();
    expect(screen.getByTestId('treeitem-package.json')).toBeInTheDocument();
  });

  it('collapses and expands a folder on click', () => {
    const providerProps = {
      artifacts: mockArtifacts,
      loading: { artifacts: false },
      error: { artifacts: null },
      refetch: () => {},
    };
    renderWithContext(<ProjectViewer />, { providerProps });

    const folder = screen.getByTestId('treeitem-src');

    // Initially expanded, so child should be visible
    expect(screen.getByTestId('treeitem-components')).toBeInTheDocument();

    // Click to collapse
    fireEvent.click(folder);
    expect(screen.queryByTestId('treeitem-components')).not.toBeInTheDocument();

    // Click to expand again
    fireEvent.click(folder);
    expect(screen.getByTestId('treeitem-components')).toBeInTheDocument();
  });

  it('shows an empty state message', () => {
    const providerProps = {
      artifacts: {},
      loading: { artifacts: false },
      error: { artifacts: null },
      refetch: () => {},
    };
    renderWithContext(<ProjectViewer />, { providerProps });
    expect(screen.getByText('No project specification generated yet.')).toBeInTheDocument();
  });
});
