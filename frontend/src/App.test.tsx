import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';

const loginResponse = {
  access_token: 'token-123',
  token_type: 'bearer',
  person_id: 5,
  is_admin: true,
};

const choresResponse = [
  {
    id: 1,
    name: 'Wash dishes',
    description: 'Wash the dishes',
    person_id: null,
    recurrence: 'none',
    recurrence_day: null,
    last_completed_date: null,
    last_completed_id: null,
    created_at: '2026-05-06T00:00:00',
    updated_at: '2026-05-06T00:00:00',
  },
];

function mockJsonResponse<T>(body: T, init?: ResponseInit): Response {
  return new Response(JSON.stringify(body), {
    headers: {
      'Content-Type': 'application/json',
    },
    ...init,
  });
}

describe('App', () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('logs in with login_name and PIN, then shows the chores dashboard', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch');
    fetchMock.mockImplementation(async (input) => {
      const url = typeof input === 'string' ? input : input instanceof Request ? input.url : String(input);
      if (url.endsWith('/auth/login')) {
        return mockJsonResponse(loginResponse);
      }
      if (url.endsWith('/chores/')) {
        return mockJsonResponse(choresResponse);
      }
      if (url.endsWith('/people/')) {
        return mockJsonResponse([]);
      }
      throw new Error(`Unexpected fetch: ${url}`);
    });

    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText(/login name/i), 'dad');
    await user.type(screen.getByLabelText(/^pin$/i), '5868');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByRole('heading', { name: /welcome, dad/i })).toBeInTheDocument();
    expect(screen.getByText('Wash dishes')).toBeInTheDocument();
    expect(screen.getByText('0 people')).toBeInTheDocument();
    expect(window.localStorage.getItem('choreboss.session')).toContain('token-123');
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
  });

  it('surfaces backend login errors', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      mockJsonResponse({ detail: 'Invalid PIN' }, { status: 401 }),
    );

    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText(/login name/i), 'dad');
    await user.type(screen.getByLabelText(/^pin$/i), '1234');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid PIN');
  });
});
