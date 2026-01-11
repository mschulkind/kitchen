/**
 * Tests for API Client 🧪
 * 
 * Tests the API wrapper functions for the Kitchen backend.
 */

import { pantryApi, healthApi, CreatePantryItem } from '../lib/api';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('Health API', () => {
    it('calls /health endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'healthy' }),
      });

      const result = await healthApi.check();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/health'),
        expect.objectContaining({
          headers: { 'Content-Type': 'application/json' },
        })
      );
      expect(result.status).toBe('healthy');
    });
  });

  describe('Pantry API', () => {
    describe('list', () => {
      it('fetches pantry items with pagination', async () => {
        const mockItems = {
          items: [{ id: '1', name: 'Rice' }],
          total: 1,
          page: 1,
          per_page: 50,
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockItems),
        });

        const result = await pantryApi.list({ page: 1, per_page: 50 });

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/pantry'),
          expect.anything()
        );
        expect(result.items).toHaveLength(1);
      });

      it('handles empty pagination params', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ items: [], total: 0 }),
        });

        await pantryApi.list();

        expect(mockFetch).toHaveBeenCalled();
      });
    });

    describe('get', () => {
      it('fetches a single item by ID', async () => {
        const mockItem = { id: 'item-123', name: 'Flour' };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockItem),
        });

        const result = await pantryApi.get('item-123');

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/pantry/item-123'),
          expect.anything()
        );
        expect(result.name).toBe('Flour');
      });
    });

    describe('create', () => {
      it('creates a new pantry item', async () => {
        const newItem: CreatePantryItem = {
          name: 'Butter',
          quantity: 1,
          unit: 'stick',
          location: 'fridge',
        };

        const mockResponse = { id: 'new-id', ...newItem };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockResponse),
        });

        const result = await pantryApi.create(newItem);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/pantry'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify(newItem),
          })
        );
        expect(result.id).toBe('new-id');
      });
    });

    describe('update', () => {
      it('updates an existing item', async () => {
        const updates = { quantity: 2.5 };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ id: 'item-1', quantity: 2.5 }),
        });

        const result = await pantryApi.update('item-1', updates);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/pantry/item-1'),
          expect.objectContaining({
            method: 'PATCH',
            body: JSON.stringify(updates),
          })
        );
        expect(result.quantity).toBe(2.5);
      });
    });

    describe('delete', () => {
      it('deletes an item', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(undefined),
        });

        await pantryApi.delete('item-to-delete');

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/pantry/item-to-delete'),
          expect.objectContaining({ method: 'DELETE' })
        );
      });
    });

    describe('search', () => {
      it('searches items by query', async () => {
        const mockResults = [
          { id: '1', name: 'Brown Rice' },
          { id: '2', name: 'White Rice' },
        ];

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockResults),
        });

        const result = await pantryApi.search('rice');

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/pantry/search?q=rice'),
          expect.anything()
        );
        expect(result).toHaveLength(2);
      });

      it('encodes special characters in query', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([]),
        });

        await pantryApi.search('salt & pepper');

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('salt%20%26%20pepper'),
          expect.anything()
        );
      });
    });

    describe('confirmPossession', () => {
      it('confirms item possession with default values', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ id: 'confirmed', name: 'Cumin' }),
        });

        const result = await pantryApi.confirmPossession('Cumin');

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('item_name=Cumin'),
          expect.objectContaining({ method: 'POST' })
        );
        expect(result.name).toBe('Cumin');
      });

      it('confirms with custom quantity and unit', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ id: 'new', name: 'Flour', quantity: 2, unit: 'kg' }),
        });

        await pantryApi.confirmPossession('Flour', 'kg', 2);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('unit=kg'),
          expect.anything()
        );
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('quantity=2'),
          expect.anything()
        );
      });
    });
  });

  describe('Error Handling', () => {
    it('throws error on non-ok response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'Not found' }),
      });

      await expect(pantryApi.get('nonexistent')).rejects.toThrow('Not found');
    });

    it('handles network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(healthApi.check()).rejects.toThrow('Network error');
    });

    it('handles malformed error response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error('Invalid JSON')),
      });

      await expect(pantryApi.list()).rejects.toThrow();
    });
  });
});
