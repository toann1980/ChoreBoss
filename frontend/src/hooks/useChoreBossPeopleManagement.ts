import type { FormEvent } from 'react';
import { useState } from 'react';
import { createPerson, deletePerson, updatePerson } from '../api';
import type { AuthSession, PersonRead } from '../types';
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

interface UseChoreBossPeopleManagementOptions {
  session: AuthSession | null;
  people: PersonRead[];
  setPeople: React.Dispatch<React.SetStateAction<PersonRead[]>>;
  onMessageChange: (message: string) => void;
}

export interface UseChoreBossPeopleManagementResult {
  personCreateForm: PersonCreateFormState;
  personEditForm: PersonEditFormState | null;
  editingPersonId: number | null;
  peopleFormError: string;
  peopleFormBusy: boolean;
  createPersonFromForm: (event: FormEvent<HTMLFormElement>) => void;
  startEditPerson: (person: PersonRead) => void;
  cancelEditPerson: () => void;
  savePerson: (personId: number) => void;
  deletePersonById: (personId: number) => void;
  updateCreateForm: (next: Partial<PersonCreateFormState>) => void;
  updateEditForm: (next: Partial<PersonEditFormState>) => void;
}

export function useChoreBossPeopleManagement({
  session,
  people,
  setPeople,
  onMessageChange,
}: UseChoreBossPeopleManagementOptions): UseChoreBossPeopleManagementResult {
  const [personCreateForm, setPersonCreateForm] = useState<PersonCreateFormState>(EMPTY_PERSON_CREATE_FORM);
  const [personEditForm, setPersonEditForm] = useState<PersonEditFormState | null>(null);
  const [editingPersonId, setEditingPersonId] = useState<number | null>(null);
  const [peopleFormError, setPeopleFormError] = useState<string>('');
  const [peopleFormBusy, setPeopleFormBusy] = useState(false);

  async function handleCreatePerson(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!session) {
      return;
    }

    setPeopleFormBusy(true);
    setPeopleFormError('');

    try {
      const createdPerson = await createPerson(session.access_token, personCreateForm);
      setPeople((current) => [...current, createdPerson]);
      setPersonCreateForm(EMPTY_PERSON_CREATE_FORM);
      onMessageChange(`Created ${createdPerson.first_name} ${createdPerson.last_name}`);
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
      const updatedPerson = await updatePerson(session.access_token, personId, personEditForm);
      setPeople((current) => current.map((person) => (person.id === updatedPerson.id ? updatedPerson : person)));
      onMessageChange(`Updated ${updatedPerson.first_name} ${updatedPerson.last_name}`);
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
      onMessageChange(`Deleted ${label}`);
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
    personCreateForm,
    personEditForm,
    editingPersonId,
    peopleFormError,
    peopleFormBusy,
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
