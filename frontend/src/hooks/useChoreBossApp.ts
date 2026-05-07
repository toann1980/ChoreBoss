import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import {
  completeChore,
  createPerson,
  deletePerson,
  loadChores,
  loadPeople,
  updatePerson,
} from '../api';
import type { ChoreRead, PersonRead } from '../types';
import { useChoreBossAuth } from './useChoreBossAuth';
import {
  type PersonCreateFormState,
  type PersonEditFormState,
} from '../components/PeoplePanel';

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

export interface UseChoreBossAppResult {
  session: ReturnType<typeof useChoreBossAuth>['session'];
  loginForm: ReturnType<typeof useChoreBossAuth>['loginForm'];
  personCreateForm: PersonCreateFormState;
  personEditForm: PersonEditFormState | null;
  editingPersonId: number | null;
  peopleFormError: string;
  peopleFormBusy: boolean;
  chores: ChoreRead[];
  people: PersonRead[];
  loading: boolean;
  dashboardLoading: boolean;
  completingChoreId: number | null;
  message: string;
  isAuthenticated: boolean;
  isAlertMessage: boolean;
  handleLogin: ReturnType<typeof useChoreBossAuth>['handleLogin'];
  handleLogout: ReturnType<typeof useChoreBossAuth>['handleLogout'];
  setLoginName: ReturnType<typeof useChoreBossAuth>['setLoginName'];
  setPin: ReturnType<typeof useChoreBossAuth>['setPin'];
  completeChoreById: (choreId: number) => void;
  createPersonFromForm: (event: FormEvent<HTMLFormElement>) => void;
  startEditPerson: (person: PersonRead) => void;
  cancelEditPerson: () => void;
  savePerson: (personId: number) => void;
  deletePersonById: (personId: number) => void;
  updateCreateForm: (next: Partial<PersonCreateFormState>) => void;
  updateEditForm: (next: Partial<PersonEditFormState>) => void;
}

export function useChoreBossApp(): UseChoreBossAppResult {
  const [message, setMessage] = useState<string>('');
  const [personCreateForm, setPersonCreateForm] = useState<PersonCreateFormState>(EMPTY_PERSON_CREATE_FORM);
  const [personEditForm, setPersonEditForm] = useState<PersonEditFormState | null>(null);
  const [editingPersonId, setEditingPersonId] = useState<number | null>(null);
  const [peopleFormError, setPeopleFormError] = useState<string>('');
  const [peopleFormBusy, setPeopleFormBusy] = useState(false);
  const [chores, setChores] = useState<ChoreRead[]>([]);
  const [people, setPeople] = useState<PersonRead[]>([]);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [completingChoreId, setCompletingChoreId] = useState<number | null>(null);

  const auth = useChoreBossAuth({
    onMessageChange: setMessage,
    onLogoutCleanup: () => {
      setChores([]);
      setPeople([]);
      setPersonCreateForm(EMPTY_PERSON_CREATE_FORM);
      setPersonEditForm(null);
      setEditingPersonId(null);
      setPeopleFormError('');
      setPeopleFormBusy(false);
      setDashboardLoading(false);
      setCompletingChoreId(null);
    },
  });

  const isAuthenticated = useMemo(() => auth.session !== null, [auth.session]);
  const isAlertMessage = useMemo(() => {
    if (!message) {
      return false;
    }

    return !message.startsWith('Welcome') && message !== 'Loading chores…' && message !== 'Signed out';
  }, [message]);

  useEffect(() => {
    const session = auth.session;
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
  }, [auth.session]);

  async function handleCompleteChore(choreId: number): Promise<void> {
    if (!auth.session) {
      return;
    }

    setCompletingChoreId(choreId);
    try {
      const updatedChore = await completeChore(auth.session.access_token, choreId);
      setChores((current) => current.map((chore) => (chore.id === updatedChore.id ? updatedChore : chore)));
      setMessage(`Completed ${updatedChore.name}`);
    } catch (error: unknown) {
      setMessage(error instanceof Error ? error.message : 'Unable to complete chore');
    } finally {
      setCompletingChoreId(null);
    }
  }

  async function handleCreatePerson(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!auth.session) {
      return;
    }

    setPeopleFormBusy(true);
    setPeopleFormError('');

    try {
      const createdPerson = await createPerson(auth.session.access_token, personCreateForm);
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
    if (!auth.session || !personEditForm) {
      return;
    }

    setPeopleFormBusy(true);
    setPeopleFormError('');

    try {
      const updatedPerson = await updatePerson(auth.session.access_token, personId, personEditForm);
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
    if (!auth.session) {
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
      await deletePerson(auth.session.access_token, personId);
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

  const updateCreateForm = (next: Partial<PersonCreateFormState>): void => {
    setPersonCreateForm((current) => ({
      ...current,
      ...next,
    }));
  };

  const updateEditForm = (next: Partial<PersonEditFormState>): void => {
    setPersonEditForm((current) => (current ? { ...current, ...next } : current));
  };

  return {
    session: auth.session,
    loginForm: auth.loginForm,
    personCreateForm,
    personEditForm,
    editingPersonId,
    peopleFormError,
    peopleFormBusy,
    chores,
    people,
    loading: auth.loading,
    dashboardLoading,
    completingChoreId,
    message,
    isAuthenticated,
    isAlertMessage,
    handleLogin: auth.handleLogin,
    handleLogout: auth.handleLogout,
    setLoginName: auth.setLoginName,
    setPin: auth.setPin,
    completeChoreById: (choreId) => {
      void handleCompleteChore(choreId);
    },
    createPersonFromForm: (event) => {
      void handleCreatePerson(event);
    },
    startEditPerson,
    cancelEditPerson,
    savePerson: (personId) => {
      void handleSavePerson(personId);
    },
    deletePersonById: (personId) => {
      void handleDeletePerson(personId);
    },
    updateCreateForm,
    updateEditForm,
  };
}
