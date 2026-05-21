import { render, screen, waitFor, within } from '@testing-library/react';
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

const peopleResponse = [
  {
    id: 5,
    first_name: 'Toan',
    last_name: 'Nguyen',
    login_name: 'dad',
    birthday: '1980-05-25',
    is_admin: true,
    sequence_num: 1,
    created_at: '2026-05-06T00:00:00',
    updated_at: '2026-05-06T00:00:00',
  },
  {
    id: 6,
    first_name: 'Kid',
    last_name: 'Nguyen',
    login_name: 'kid',
    birthday: '2010-01-01',
    is_admin: false,
    sequence_num: 2,
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

  it('logs in with login_name and PIN, then shows the chores dashboard and people list', async () => {
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
        return mockJsonResponse(peopleResponse);
      }
      throw new Error(`Unexpected fetch: ${url}`);
    });

    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getAllByLabelText(/login name/i)[0], 'dad');
    await user.type(screen.getAllByLabelText(/^pin$/i)[0], '5868');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByRole('heading', { name: /welcome, dad/i })).toBeInTheDocument();
    expect(await screen.findByText('Wash dishes')).toBeInTheDocument();
    expect(screen.getByText('2 people')).toBeInTheDocument();
    expect(await screen.findByText('Toan Nguyen', { selector: 'strong' })).toBeInTheDocument();
    expect(await screen.findByText('Kid Nguyen', { selector: 'strong' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add person/i })).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /edit/i })[0]).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /delete/i })[0]).toBeInTheDocument();
    expect(window.localStorage.getItem('choreboss.session')).toContain('token-123');
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
  });

  it('creates, edits, and deletes people from the admin dashboard', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch');
    fetchMock.mockImplementation(async (input, init) => {
      const url = typeof input === 'string' ? input : input instanceof Request ? input.url : String(input);
      if (url.endsWith('/auth/login')) {
        return mockJsonResponse(loginResponse);
      }
      if (url.endsWith('/chores/')) {
        return mockJsonResponse(choresResponse);
      }
      if (url.endsWith('/people/') && init?.method === 'POST') {
        return mockJsonResponse({
          id: 7,
          first_name: 'New',
          last_name: 'Person',
          login_name: 'new-person',
          birthday: '2010-02-02',
          is_admin: false,
          sequence_num: 3,
          created_at: '2026-05-06T00:00:00',
          updated_at: '2026-05-06T00:00:00',
        });
      }
      if (url.endsWith('/people/')) {
        return mockJsonResponse(peopleResponse);
      }
      if (url.endsWith('/people/5') && init?.method === 'PUT') {
        return mockJsonResponse({
          id: 5,
          first_name: 'Toan',
          last_name: 'Nguyen',
          login_name: 'dad',
          birthday: '1980-05-26',
          is_admin: true,
          sequence_num: 1,
          created_at: '2026-05-06T00:00:00',
          updated_at: '2026-05-06T00:00:00',
        });
      }
      if (url.endsWith('/people/5') && init?.method === 'DELETE') {
        return new Response(null, { status: 204 });
      }
      throw new Error(`Unexpected fetch: ${url}`);
    });

    vi.spyOn(window, 'confirm').mockReturnValue(true);

    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getAllByLabelText(/login name/i)[0], 'dad');
    await user.type(screen.getAllByLabelText(/^pin$/i)[0], '5868');
    await user.click(screen.getByRole('button', { name: /sign in/i }));
    await screen.findAllByRole('button', { name: /edit/i });

    await user.type(screen.getAllByLabelText(/first name/i)[0], 'New');
    await user.type(screen.getAllByLabelText(/^last name$/i)[0], 'Person');
    await user.type(screen.getAllByLabelText(/^login name$/i)[0], 'new-person');
    await user.type(screen.getAllByLabelText(/^birthday$/i)[0], '2010-02-02');
    await user.type(screen.getAllByLabelText(/^pin$/i)[1], '1234');
    await user.click(screen.getAllByRole('button', { name: /add person/i })[0]);

    expect(await screen.findByText('New Person')).toBeInTheDocument();
    expect(screen.getByText('@new-person')).toBeInTheDocument();

    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    await user.click(editButtons[0]);
    const birthdayInputs = screen.getAllByLabelText(/^birthday$/i);
    await user.clear(birthdayInputs[1]);
    await user.type(birthdayInputs[1], '1980-05-26');
    const saveButtons = screen.getAllByRole('button', { name: /save/i });
    await user.click(saveButtons[0]);

    expect(await screen.findByText('Updated Toan Nguyen')).toBeInTheDocument();

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    await user.click(deleteButtons[0]);

    expect(await screen.findByText('Deleted Toan Nguyen')).toBeInTheDocument();
    await waitFor(() => {
      const mains = screen.getAllByRole('main');
      const activeMain = mains[mains.length - 1];
      expect(within(activeMain).getAllByRole('button', { name: /delete/i })).toHaveLength(2);
    });
  });

  it('surfaces backend login errors', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      mockJsonResponse({ detail: 'Invalid PIN' }, { status: 401 }),
    );

    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getAllByLabelText(/login name/i)[0], 'dad');
    await user.type(screen.getAllByLabelText(/^pin$/i)[0], '1234');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText('Invalid PIN')).toBeInTheDocument();
  });
});
