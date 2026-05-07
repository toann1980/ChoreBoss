import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { completeChore, loadChores, loadPeople } from '../api';
import type { AuthSession, ChoreRead, PersonRead } from '../types';
import { useChoreBossPeopleManagement } from './useChoreBossPeopleManagement';

interface UseChoreBossDashboardOptions {
  session: AuthSession | null;
  onMessageChange: (message: string) => void;
}

export interface UseChoreBossDashboardResult {
  personCreateForm: import('../components/PeoplePanel').PersonCreateFormState;
  personEditForm: import('../components/PeoplePanel').PersonEditFormState | null;
  editingPersonId: number | null;
  peopleFormError: string;
  peopleFormBusy: boolean;
  chores: ChoreRead[];
  people: PersonRead[];
  dashboardLoading: boolean;
  completingChoreId: number | null;
  completeChoreById: (choreId: number) => void;
  createPersonFromForm: (event: FormEvent<HTMLFormElement>) => void;
  startEditPerson: (person: PersonRead) => void;
  cancelEditPerson: () => void;
  savePerson: (personId: number) => void;
  deletePersonById: (personId: number) => void;
  updateCreateForm: (next: Partial<import('../components/PeoplePanel').PersonCreateFormState>) => void;
  updateEditForm: (next: Partial<import('../components/PeoplePanel').PersonEditFormState>) => void;
}

export function useChoreBossDashboard({ session, onMessageChange }: UseChoreBossDashboardOptions): UseChoreBossDashboardResult {
  const [chores, setChores] = useState<ChoreRead[]>([]);
  const [people, setPeople] = useState<PersonRead[]>([]);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [completingChoreId, setCompletingChoreId] = useState<number | null>(null);

  const peopleManagement = useChoreBossPeopleManagement({
    session,
    people,
    setPeople,
    onMessageChange,
  });

  useEffect(() => {
    if (!session) {
      return;
    }

    let isCurrent = true;

    const run = async (): Promise<void> => {
      setDashboardLoading(true);
      onMessageChange('Loading chores…');

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
        onMessageChange(`Welcome, ${session.loginName}`);
      } catch (error: unknown) {
        if (!isCurrent) {
          return;
        }
        onMessageChange(error instanceof Error ? error.message : 'Failed to load chores');
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
  }, [session, onMessageChange]);

  async function handleCompleteChore(choreId: number): Promise<void> {
    if (!session) {
      return;
    }

    setCompletingChoreId(choreId);
    try {
      const updatedChore = await completeChore(session.access_token, choreId);
      setChores((current) => current.map((chore) => (chore.id === updatedChore.id ? updatedChore : chore)));
      onMessageChange(`Completed ${updatedChore.name}`);
    } catch (error: unknown) {
      onMessageChange(error instanceof Error ? error.message : 'Unable to complete chore');
    } finally {
      setCompletingChoreId(null);
    }
  }

  return {
    personCreateForm: peopleManagement.personCreateForm,
    personEditForm: peopleManagement.personEditForm,
    editingPersonId: peopleManagement.editingPersonId,
    peopleFormError: peopleManagement.peopleFormError,
    peopleFormBusy: peopleManagement.peopleFormBusy,
    chores,
    people,
    dashboardLoading,
    completingChoreId,
    completeChoreById: (choreId) => {
      void handleCompleteChore(choreId);
    },
    createPersonFromForm: peopleManagement.createPersonFromForm,
    startEditPerson: peopleManagement.startEditPerson,
    cancelEditPerson: peopleManagement.cancelEditPerson,
    savePerson: peopleManagement.savePerson,
    deletePersonById: peopleManagement.deletePersonById,
    updateCreateForm: peopleManagement.updateCreateForm,
    updateEditForm: peopleManagement.updateEditForm,
  };
}
