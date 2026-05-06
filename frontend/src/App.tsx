import { useEffect, useMemo, useState } from 'react';
import {
  ApiError,
  completeChore,
  createPerson,
  deletePerson,
  login,
  loadChores,
  loadPeople,
  updatePerson,
  toSession,
} from './api';
import './App.css';
import type {
  AuthSession,
  ChoreRead,
  PersonCreateInput,
  PersonRead,
  PersonUpdateInput,
} from './types';

const STORAGE_KEY = 'choreboss.session';

interface LoginFormState {
  loginName: string;
  pin: string;
}

interface PersonCreateFormState {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  pin: string;
  is_admin: boolean;
}

interface PersonEditFormState {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  is_admin: boolean;
}

const EMPTY_PERSON_CREATE_FORM: PersonCreateFormState = {
  first_name: '',
  last_name: '',
  login_name: '',
  birthday: '',
  pin: '',
  is_admin: false,
};

function personToEditForm(person: PersonRead): PersonEditFormState {
  return {
    first_name: person.first_name,
    last_name: person.last_name,
    login_name: person.login_name,
    birthday: person.birthday,
    is_admin: person.is_admin,
  };
}

function readSession(): AuthSession | null {
  const rawSession = window.localStorage.getItem(STORAGE_KEY);
  if (!rawSession) {
    return null;
  }

  try {
    return JSON.parse(rawSession) as AuthSession;
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

function App() {
  const [session, setSession] = useState<AuthSession | null>(() => readSession());
  const [loginForm, setLoginForm] = useState<LoginFormState>({
    loginName: '',
    pin: '',
  });
  const [personCreateForm, setPersonCreateForm] = useState<PersonCreateFormState>(EMPTY_PERSON_CREATE_FORM);
  const [personEditForm, setPersonEditForm] = useState<PersonEditFormState | null>(null);
  const [editingPersonId, setEditingPersonId] = useState<number | null>(null);
  const [peopleFormError, setPeopleFormError] = useState<string>('');
  const [peopleFormBusy, setPeopleFormBusy] = useState(false);
  const [chores, setChores] = useState<ChoreRead[]>([]);
  const [people, setPeople] = useState<PersonRead[]>([]);
  const [loading, setLoading] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [completingChoreId, setCompletingChoreId] = useState<number | null>(null);
  const [message, setMessage] = useState<string>('');
  const isAuthenticated = useMemo(() => session !== null, [session]);
  const isAlertMessage = useMemo(() => {
    if (!message) {
      return false;
    }

    return !message.startsWith('Welcome') && message !== 'Loading chores…' && message !== 'Signed out';
  }, [message]);

  useEffect(() => {
    if (!session) {
      return;
    }

    let isCurrent = true;

    const run = async (): Promise<void> => {
      setDashboardLoading(true);
      setMessage('Loading chores…');

      try {
        const [nextChores, nextPeople] = await Promise.all([
          loadChores(session.access_token),
          loadPeople(session.access_token),
        ]);
        if (!isCurrent) {
          return;
        }
        setChores(nextChores);
        setPeople(nextPeople);
        setMessage(`Welcome, ${session.loginName}`);
      } catch (error: unknown) {
        if (!isCurrent) {
          return;
        }
        setMessage(error instanceof Error ? error.message : 'Failed to load chores');
      } finally {
        if (isCurrent) {
          setDashboardLoading(false);
        }
      }
    };

    void run();

    return () => {
      isCurrent = false;
    };
  }, [session]);

  async function handleLogin(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const loginResponse = await login(loginForm.loginName, loginForm.pin);
      const nextSession = toSession(loginForm.loginName, loginResponse);
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
      setSession(nextSession);
    } catch (error: unknown) {
      const text = error instanceof ApiError ? error.message : 'Unable to sign in';
      setMessage(text);
    } finally {
      setLoading(false);
    }
  }

  async function handleCompleteChore(choreId: number): Promise<void> {
    if (!session) {
      return;
    }

    setCompletingChoreId(choreId);
    try {
      const updatedChore = await completeChore(session.access_token, choreId);
      setChores((current) => current.map((chore) => (chore.id === updatedChore.id ? updatedChore : chore)));
      setMessage(`Completed ${updatedChore.name}`);
    } catch (error: unknown) {
      setMessage(error instanceof Error ? error.message : 'Unable to complete chore');
    } finally {
      setCompletingChoreId(null);
    }
  }

  async function handleCreatePerson(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!session) {
      return;
    }

    setPeopleFormBusy(true);
    setPeopleFormError('');

    try {
      const createdPerson = await createPerson(
        session.access_token,
        personCreateForm as PersonCreateInput,
      );
      setPeople((current) => [...current, createdPerson]);
      setPersonCreateForm(EMPTY_PERSON_CREATE_FORM);
      setMessage(`Created ${createdPerson.first_name} ${createdPerson.last_name}`);
    } catch (error: unknown) {
      setPeopleFormError(error instanceof Error ? error.message : 'Unable to create person');
    } finally {
      setPeopleFormBusy(false);
    }
  }

  function startEditPerson(person: PersonRead): void {
    setEditingPersonId(person.id);
    setPersonEditForm(personToEditForm(person));
    setPeopleFormError('');
  }

  function cancelEditPerson(): void {
    setEditingPersonId(null);
    setPersonEditForm(null);
    setPeopleFormError('');
  }

  async function handleSavePerson(personId: number): Promise<void> {
    if (!session || !personEditForm) {
      return;
    }

    setPeopleFormBusy(true);
    setPeopleFormError('');

    try {
      const updatedPerson = await updatePerson(session.access_token, personId, personEditForm as PersonUpdateInput);
      setPeople((current) => current.map((person) => (person.id === updatedPerson.id ? updatedPerson : person)));
      setMessage(`Updated ${updatedPerson.first_name} ${updatedPerson.last_name}`);
      cancelEditPerson();
    } catch (error: unknown) {
      setPeopleFormError(error instanceof Error ? error.message : 'Unable to update person');
    } finally {
      setPeopleFormBusy(false);
    }
  }

  async function handleDeletePerson(personId: number): Promise<void> {
    if (!session) {
      return;
    }

    const person = people.find((candidate) => candidate.id === personId);
    const label = person ? `${person.first_name} ${person.last_name}` : `person ${personId}`;
    const confirmed = window.confirm(`Delete ${label}?`);
    if (!confirmed) {
      return;
    }

    setPeopleFormBusy(true);
    setPeopleFormError('');

    try {
      await deletePerson(session.access_token, personId);
      setPeople((current) => current.filter((candidate) => candidate.id !== personId));
      setMessage(`Deleted ${label}`);
      if (editingPersonId === personId) {
        cancelEditPerson();
      }
    } catch (error: unknown) {
      setPeopleFormError(error instanceof Error ? error.message : 'Unable to delete person');
    } finally {
      setPeopleFormBusy(false);
    }
  }

  function handleLogout(): void {
    window.localStorage.removeItem(STORAGE_KEY);
    setSession(null);
    setChores([]);
    setPeople([]);
    setPersonCreateForm(EMPTY_PERSON_CREATE_FORM);
    setPersonEditForm(null);
    setEditingPersonId(null);
    setPeopleFormError('');
    setLoginForm({ loginName: '', pin: '' });
    setMessage('Signed out');
  }

  return (
    <main className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">ChoreBoss</p>
          <h1>TypeScript frontend</h1>
          <p className="subhead">
            FastAPI backend, typed UI, and a clean path away from the Flask bridge.
          </p>
        </div>
        {session ? (
          <button type="button" className="secondary-button" onClick={handleLogout}>
            Sign out
          </button>
        ) : null}
      </header>

      {isAuthenticated ? (
        <section className="panel" aria-live="polite">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Dashboard</p>
              <h2>Welcome, {session?.loginName}</h2>
            </div>
            <span className={session?.is_admin ? 'badge badge-admin' : 'badge'}>
              {session?.is_admin ? 'Admin' : 'Member'}
            </span>
          </div>

          <p className="status" role={isAlertMessage ? 'alert' : undefined}>
            {message}
          </p>
          {peopleFormError ? (
            <p className="status" role="alert">
              {peopleFormError}
            </p>
          ) : null}

          <div className="list-card">
            <div className="list-card-header">
              <h3>Chores</h3>
              {dashboardLoading ? <span>Loading…</span> : <span>{chores.length} items</span>}
            </div>
            <ul className="chore-list">
              {chores.map((chore) => (
                <li key={chore.id}>
                  <strong>{chore.name}</strong>
                  <p>{chore.description}</p>
                  <button
                    type="button"
                    className="secondary-button chore-action"
                    disabled={completingChoreId === chore.id}
                    onClick={() => {
                      void handleCompleteChore(chore.id);
                    }}
                  >
                    {completingChoreId === chore.id ? 'Completing…' : 'Mark complete'}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="list-card">
            <div className="list-card-header">
              <h3>People</h3>
              {dashboardLoading ? <span>Loading…</span> : <span>{people.length} people</span>}
            </div>

            {session?.is_admin ? (
              <form className="people-form" onSubmit={handleCreatePerson}>
                <h4>Add person</h4>
                <div className="people-form-grid">
                  <label>
                    First name
                    <input
                      name="first_name"
                      value={personCreateForm.first_name}
                      onChange={(event) =>
                        setPersonCreateForm((current) => ({
                          ...current,
                          first_name: event.target.value,
                        }))
                      }
                    />
                  </label>
                  <label>
                    Last name
                    <input
                      name="last_name"
                      value={personCreateForm.last_name}
                      onChange={(event) =>
                        setPersonCreateForm((current) => ({
                          ...current,
                          last_name: event.target.value,
                        }))
                      }
                    />
                  </label>
                  <label>
                    Login name
                    <input
                      name="login_name"
                      value={personCreateForm.login_name}
                      onChange={(event) =>
                        setPersonCreateForm((current) => ({
                          ...current,
                          login_name: event.target.value,
                        }))
                      }
                    />
                  </label>
                  <label>
                    Birthday
                    <input
                      name="birthday"
                      type="date"
                      value={personCreateForm.birthday}
                      onChange={(event) =>
                        setPersonCreateForm((current) => ({
                          ...current,
                          birthday: event.target.value,
                        }))
                      }
                    />
                  </label>
                  <label>
                    PIN
                    <input
                      name="pin"
                      type="password"
                      inputMode="numeric"
                      value={personCreateForm.pin}
                      onChange={(event) =>
                        setPersonCreateForm((current) => ({
                          ...current,
                          pin: event.target.value,
                        }))
                      }
                    />
                  </label>
                  <label className="checkbox-row">
                    <input
                      name="is_admin"
                      type="checkbox"
                      checked={personCreateForm.is_admin}
                      onChange={(event) =>
                        setPersonCreateForm((current) => ({
                          ...current,
                          is_admin: event.target.checked,
                        }))
                      }
                    />
                    Admin
                  </label>
                </div>
                <button type="submit" disabled={peopleFormBusy}>
                  {peopleFormBusy ? 'Saving…' : 'Add person'}
                </button>
              </form>
            ) : null}

            <ul className="people-list">
              {people.map((person) => {
                const isEditing = editingPersonId === person.id;
                return (
                  <li key={person.id}>
                    {isEditing && personEditForm ? (
                      <div className="people-edit-form">
                        <div className="people-form-grid">
                          <label>
                            First name
                            <input
                              value={personEditForm.first_name}
                              onChange={(event) =>
                                setPersonEditForm((current) =>
                                  current ? { ...current, first_name: event.target.value } : current,
                                )
                              }
                            />
                          </label>
                          <label>
                            Last name
                            <input
                              value={personEditForm.last_name}
                              onChange={(event) =>
                                setPersonEditForm((current) =>
                                  current ? { ...current, last_name: event.target.value } : current,
                                )
                              }
                            />
                          </label>
                          <label>
                            Login name
                            <input
                              value={personEditForm.login_name}
                              onChange={(event) =>
                                setPersonEditForm((current) =>
                                  current ? { ...current, login_name: event.target.value } : current,
                                )
                              }
                            />
                          </label>
                          <label>
                            Birthday
                            <input
                              type="date"
                              value={personEditForm.birthday}
                              onChange={(event) =>
                                setPersonEditForm((current) =>
                                  current ? { ...current, birthday: event.target.value } : current,
                                )
                              }
                            />
                          </label>
                          <label className="checkbox-row">
                            <input
                              type="checkbox"
                              checked={personEditForm.is_admin}
                              onChange={(event) =>
                                setPersonEditForm((current) =>
                                  current ? { ...current, is_admin: event.target.checked } : current,
                                )
                              }
                            />
                            Admin
                          </label>
                        </div>
                        <div className="people-actions">
                          <button
                            type="button"
                            className="secondary-button"
                            disabled={peopleFormBusy}
                            onClick={() => {
                              void handleSavePerson(person.id);
                            }}
                          >
                            {peopleFormBusy ? 'Saving…' : 'Save'}
                          </button>
                          <button
                            type="button"
                            className="secondary-button"
                            disabled={peopleFormBusy}
                            onClick={cancelEditPerson}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <strong>
                          {person.first_name} {person.last_name}
                        </strong>
                        <p>@{person.login_name}</p>
                        <span className={person.is_admin ? 'badge badge-admin' : 'badge'}>
                          {person.is_admin ? 'Admin' : 'Member'}
                        </span>
                        {session?.is_admin ? (
                          <div className="people-actions">
                            <button
                              type="button"
                              className="secondary-button"
                              onClick={() => startEditPerson(person)}
                            >
                              Edit
                            </button>
                            <button
                              type="button"
                              className="secondary-button"
                              disabled={peopleFormBusy}
                              onClick={() => {
                                void handleDeletePerson(person.id);
                              }}
                            >
                              Delete
                            </button>
                          </div>
                        ) : null}
                      </>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        </section>
      ) : (
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Sign in</p>
              <h2>Use your login name and PIN</h2>
            </div>
          </div>

          <form className="login-form" onSubmit={handleLogin}>
            <label>
              Login name
              <input
                name="loginName"
                autoComplete="username"
                value={loginForm.loginName}
                onChange={(event) =>
                  setLoginForm((current) => ({
                    ...current,
                    loginName: event.target.value,
                  }))
                }
              />
            </label>

            <label>
              PIN
              <input
                name="pin"
                type="password"
                inputMode="numeric"
                autoComplete="current-password"
                value={loginForm.pin}
                onChange={(event) =>
                  setLoginForm((current) => ({
                    ...current,
                    pin: event.target.value,
                  }))
                }
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="status" role={isAlertMessage ? 'alert' : undefined}>
            {message}
          </p>
        </section>
      )}
    </main>
  );
}

export default App;
