import type { FormEvent } from 'react';
import { ChoreList } from '../components/ChoreList';
import { PeoplePanel } from '../components/PeoplePanel';
import type { PersonRead } from '../types';

interface PersonCreateFormState {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  pin: string;
  is_admin: boolean;
  assign_chores: boolean;
}

interface PersonEditFormState {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  is_admin: boolean;
  assign_chores: boolean;
}

interface DashboardPageProps {
  loginName: string;
  isAdmin: boolean;
  chores: import('../types').ChoreRead[];
  people: PersonRead[];
  message: string;
  peopleFormError: string;
  dashboardLoading: boolean;
  peopleFormBusy: boolean;
  completingChoreId: number | null;
  editingPersonId: number | null;
  personCreateForm: PersonCreateFormState;
  personEditForm: PersonEditFormState | null;
  isAlertMessage: boolean;
  onCompleteChore: (choreId: number) => void;
  onCreatePerson: (event: FormEvent<HTMLFormElement>) => void;
  onEditPerson: (person: PersonRead) => void;
  onCancelEditPerson: () => void;
  onSavePerson: (personId: number) => void;
  onDeletePerson: (personId: number) => void;
  onCreateFormChange: (next: Partial<PersonCreateFormState>) => void;
  onEditFormChange: (next: Partial<PersonEditFormState>) => void;
}

export function DashboardPage({
  loginName,
  isAdmin,
  chores,
  people,
  message,
  peopleFormError,
  dashboardLoading,
  peopleFormBusy,
  completingChoreId,
  editingPersonId,
  personCreateForm,
  personEditForm,
  isAlertMessage,
  onCompleteChore,
  onCreatePerson,
  onEditPerson,
  onCancelEditPerson,
  onSavePerson,
  onDeletePerson,
  onCreateFormChange,
  onEditFormChange,
}: DashboardPageProps) {
  return (
    <section className="panel" aria-live="polite">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h2>Welcome, {loginName}</h2>
        </div>
        <span className={isAdmin ? 'badge badge-admin' : 'badge'}>{isAdmin ? 'Admin' : 'Member'}</span>
      </div>

      <p className="status" role={isAlertMessage ? 'alert' : undefined}>
        {message}
      </p>
      <ChoreList
        chores={chores}
        dashboardLoading={dashboardLoading}
        completingChoreId={completingChoreId}
        onCompleteChore={onCompleteChore}
      />

      <PeoplePanel
        people={people}
        message={message}
        peopleFormError={peopleFormError}
        dashboardLoading={dashboardLoading}
        peopleFormBusy={peopleFormBusy}
        editingPersonId={editingPersonId}
        personCreateForm={personCreateForm}
        personEditForm={personEditForm}
        isAlertMessage={isAlertMessage}
        isAdmin={isAdmin}
        onCreatePerson={onCreatePerson}
        onEditPerson={onEditPerson}
        onCancelEditPerson={onCancelEditPerson}
        onSavePerson={onSavePerson}
        onDeletePerson={onDeletePerson}
        onCreateFormChange={onCreateFormChange}
        onEditFormChange={onEditFormChange}
      />
    </section>
  );
}
