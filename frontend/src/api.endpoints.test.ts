import { describe, expect, it, vi } from 'vitest';
import { API_ENDPOINTS } from './endpoints';
import { ApiError, loadChores, loadPeople, login } from './api';

describe('api endpoint validity', () => {
  it('keeps the FastAPI endpoint paths aligned', () => {
    expect(API_ENDPOINTS.authLogin).toBe('/auth/login');
    expect(API_ENDPOINTS.people).toBe('/people/');
    expect(API_ENDPOINTS.chores).toBe('/chores/');
    expect(API_ENDPOINTS.personById(7)).toBe('/people/7');
    expect(API_ENDPOINTS.choreById(9)).toBe('/chores/9');
    expect(API_ENDPOINTS.choreComplete(9)).toBe('/chores/9/complete');
  });

  it('targets the FastAPI auth login endpoint', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({
        access_token: 'token',
        token_type: 'bearer',
        person_id: 5,
        is_admin: true,
      })),
    );

    await login('dad', '5868');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(API_ENDPOINTS.authLogin),
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('targets the FastAPI chores list endpoint', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify([])),
    );

    await loadChores('token');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(API_ENDPOINTS.chores),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer token' }),
      }),
    );
  });

  it('targets the FastAPI people list endpoint', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify([])),
    );

    await loadPeople('token');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(API_ENDPOINTS.people),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer token' }),
      }),
    );
  });

  it('maps backend error payloads into ApiError instances', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'Person not found' }), { status: 404 }),
    );

    await expect(loadPeople('token')).rejects.toMatchObject({
      name: 'ApiError',
      status: 404,
      message: 'Person not found',
    } satisfies Partial<ApiError>);
  });
});
