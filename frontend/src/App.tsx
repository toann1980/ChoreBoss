import { useEffect, useMemo, useState } from 'react';
import { ApiError, completeChore, login, loadChores, loadPeople, toSession } from './api';
import './App.css';
import type { AuthSession, ChoreRead, PersonRead } from './types';

const STORAGE_KEY = 'choreboss.session';

interface LoginFormState {
  loginName: string;
  pin: string;
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

  function handleLogout(): void {
    window.localStorage.removeItem(STORAGE_KEY);
    setSession(null);
    setChores([]);
    setPeople([]);
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
            <ul className="people-list">
              {people.map((person) => (
                <li key={person.id}>
                  <strong>
                    {person.first_name} {person.last_name}
                  </strong>
                  <p>@{person.login_name}</p>
                  <span className={person.is_admin ? 'badge badge-admin' : 'badge'}>
                    {person.is_admin ? 'Admin' : 'Member'}
                  </span>
                </li>
              ))}
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
