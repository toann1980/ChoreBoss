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
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
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

  const updateCreateForm = (next: Partial<PersonCreateInput>): void => {
    setPersonCreateForm((current) => ({
      ...current,
      ...next,
    }));
  };

  const updateEditForm = (next: Partial<PersonUpdateInput>): void => {
    setPersonEditForm((current) => (current ? { ...current, ...next } : current));
  };

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

      {isAuthenticated && session ? (
        <DashboardPage
          loginName={session.loginName}
          isAdmin={session.is_admin}
          chores={chores}
          people={people}
          message={message}
          peopleFormError={peopleFormError}
          dashboardLoading={dashboardLoading}
          peopleFormBusy={peopleFormBusy}
          completingChoreId={completingChoreId}
          editingPersonId={editingPersonId}
          personCreateForm={personCreateForm}
          personEditForm={personEditForm}
          isAlertMessage={isAlertMessage}
          onCompleteChore={(choreId) => {
            void handleCompleteChore(choreId);
          }}
          onCreatePerson={(event) => {
            void handleCreatePerson(event);
          }}
          onEditPerson={startEditPerson}
          onCancelEditPerson={cancelEditPerson}
          onSavePerson={(personId) => {
            void handleSavePerson(personId);
          }}
          onDeletePerson={(personId) => {
            void handleDeletePerson(personId);
          }}
          onCreateFormChange={updateCreateForm}
          onEditFormChange={updateEditForm}
        />
      ) : (
        <LoginPage
          loginName={loginForm.loginName}
          pin={loginForm.pin}
          loading={loading}
          message={message}
          isAlertMessage={isAlertMessage}
          onLoginNameChange={(value) => setLoginForm((current) => ({ ...current, loginName: value }))}
          onPinChange={(value) => setLoginForm((current) => ({ ...current, pin: value }))}
          onSubmit={(event) => {
            void handleLogin(event);
          }}
        />
      )}
    </main>
  );
}

export default App;
