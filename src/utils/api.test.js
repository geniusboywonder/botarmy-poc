import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchTasks, respondToAction } from './api';

// Mock the global fetch function
global.fetch = vi.fn();

describe('API utility functions', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('fetchTasks', () => {
    it('should fetch tasks for a given project ID', async () => {
      const mockTasks = { actions: [{ id: 'task1', title: 'Test Task' }] };
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTasks),
      });

      const tasks = await fetchTasks('proj_123');
      expect(fetch).toHaveBeenCalledWith('/api/projects/proj_123/actions');
      expect(tasks).toEqual(mockTasks.actions);
    });

    it('should return an empty array if no project ID is provided', async () => {
      const tasks = await fetchTasks(null);
      expect(fetch).not.toHaveBeenCalled();
      expect(tasks).toEqual([]);
    });
  });

  describe('respondToAction', () => {
    it('should send a POST request with the action response', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'resolved' }),
      });

      await respondToAction('action1', 'approve');
      expect(fetch).toHaveBeenCalledWith('/api/actions/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: 'action1', response: 'approve' }),
      });
    });
  });
});
