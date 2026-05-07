import { useState } from 'react';
import { completeChore } from '../api';
import type { AuthSession, PersonRead } from '../types';
import { useChoreBossDashboardData } from './useChoreBossDashboardData';
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
  chores: import('../types').ChoreRead[];
  people: PersonRead[];
  dashboardLoading: boolean;
  completingChoreId: number | null;
  completeChoreById: (choreId: number) => void;
  createPersonFromForm: import('react').FormEventHandler<HTMLFormElement>;
  startEditPerson: (person: PersonRead) => void;
  cancelEditPerson: () => void;
  savePerson: (personId: number) => void;
  deletePersonById: (personId: number) => void;
  updateCreateForm: (next: Partial<import('../components/PeoplePanel').PersonCreateFormState>) => void;
  updateEditForm: (next: Partial<import('../components/PeoplePanel').PersonEditFormState>) => void;
}

export function useChoreBossDashboard({ session, onMessageChange }: UseChoreBossDashboardOptions): UseChoreBossDashboardResult {
  const [completingChoreId, setCompletingChoreId] = useState<number | null>(null);
  const data = useChoreBossDashboardData({
    session,
    onMessageChange,
  });
  const peopleManagement = useChoreBossPeopleManagement({
    session,
    people: data.people,
    setPeople: data.setPeople,
    onMessageChange,
  });

  async function handleCompleteChore(choreId: number): Promise<void> {
    if (!session) {
      return;
    }

    setCompletingChoreId(choreId);
    try {
      const updatedChore = await completeChore(session.access_token, choreId);
      data.setChores((current) => current.map((chore) => (chore.id === updatedChore.id ? updatedChore : chore)));
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
    chores: data.chores,
    people: data.people,
    dashboardLoading: data.dashboardLoading,
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
