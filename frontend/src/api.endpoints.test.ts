import { describe, expect, it, vi } from 'vitest';
import { API_ENDPOINTS } from './endpoints';
import {
  ApiError,
  createPerson,
  deletePerson,
  getPerson,
  loadChores,
  loadPeople,
  login,
  updatePerson,
} from './api';

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

  it('targets the FastAPI person detail, create, update, and delete endpoints', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch');

    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({
        id: 5,
        first_name: 'Toan',
        last_name: 'Nguyen',
        login_name: 'dad',
        birthday: '1980-05-25',
        is_admin: true,
        sequence_num: 1,
        created_at: '2026-05-06T00:00:00',
        updated_at: '2026-05-06T00:00:00',
      })),
    );
    await getPerson('token', 5);
    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining(API_ENDPOINTS.personById(5)),
      expect.objectContaining({ method: 'GET' }),
    );

    fetchMock.mockClear();
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({
        id: 6,
        first_name: 'New',
        last_name: 'Person',
        login_name: 'new-person',
        birthday: '2010-01-01',
        is_admin: false,
        sequence_num: 2,
        created_at: '2026-05-06T00:00:00',
        updated_at: '2026-05-06T00:00:00',
      })),
    );
    await createPerson('token', {
      first_name: 'New',
      last_name: 'Person',
      login_name: 'new-person',
      birthday: '2010-01-01',
      pin: '1234',
    });
    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining(API_ENDPOINTS.people),
      expect.objectContaining({ method: 'POST' }),
    );

    fetchMock.mockClear();
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({
        id: 6,
        first_name: 'Updated',
        last_name: 'Person',
        login_name: 'new-person',
        birthday: '2010-01-02',
        is_admin: true,
        sequence_num: 2,
        created_at: '2026-05-06T00:00:00',
        updated_at: '2026-05-06T00:00:00',
      })),
    );
    await updatePerson('token', 6, { first_name: 'Updated', is_admin: true });
    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining(API_ENDPOINTS.personById(6)),
      expect.objectContaining({ method: 'PUT' }),
    );

    fetchMock.mockClear();
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
    await deletePerson('token', 6);
    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining(API_ENDPOINTS.personById(6)),
      expect.objectContaining({ method: 'DELETE' }),
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
