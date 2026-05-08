import type { FormEvent } from 'react';
import { PersonCreateForm } from './PersonCreateForm';
import { PersonRow } from './PersonRow';
import type { PersonRead } from '../types';

export interface PersonCreateFormState {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  pin: string;
  is_admin: boolean;
  assign_chores: boolean;
}

export interface PersonEditFormState {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  is_admin: boolean;
  assign_chores: boolean;
}

interface PeoplePanelProps {
  people: PersonRead[];
  message: string;
  peopleFormError: string;
  dashboardLoading: boolean;
  peopleFormBusy: boolean;
  editingPersonId: number | null;
  personCreateForm: PersonCreateFormState;
  personEditForm: PersonEditFormState | null;
  isAlertMessage: boolean;
  isAdmin: boolean;
  onCreatePerson: (event: FormEvent<HTMLFormElement>) => void;
  onEditPerson: (person: PersonRead) => void;
  onCancelEditPerson: () => void;
  onSavePerson: (personId: number) => void;
  onDeletePerson: (personId: number) => void;
  onCreateFormChange: (next: Partial<PersonCreateFormState>) => void;
  onEditFormChange: (next: Partial<PersonEditFormState>) => void;
}

function peopleCountLabel(count: number): string {
  return count === 1 ? '1 person' : `${count} people`;
}

export function PeoplePanel({
  people,
  peopleFormError,
  dashboardLoading,
  peopleFormBusy,
  editingPersonId,
  personCreateForm,
  personEditForm,
  isAdmin,
  onCreatePerson,
  onEditPerson,
  onCancelEditPerson,
  onSavePerson,
  onDeletePerson,
  onCreateFormChange,
  onEditFormChange,
}: PeoplePanelProps) {
  return (
    <div className="list-card">
      <div className="list-card-header">
        <h3>People</h3>
        {dashboardLoading ? <span>Loading…</span> : <span>{peopleCountLabel(people.length)}</span>}
      </div>

      {isAdmin ? (
        <PersonCreateForm busy={peopleFormBusy} form={personCreateForm} onSubmit={onCreatePerson} onChange={onCreateFormChange} />
      ) : null}

      {peopleFormError ? (
        <p className="status" role="alert">
          {peopleFormError}
        </p>
      ) : null}

      <ul className="people-list">
        {people.map((person) => (
          <PersonRow
            key={person.id}
            person={person}
            isAdmin={isAdmin}
            isEditing={editingPersonId === person.id}
            peopleFormBusy={peopleFormBusy}
            personEditForm={personEditForm}
            onEditPerson={onEditPerson}
            onCancelEditPerson={onCancelEditPerson}
            onSavePerson={onSavePerson}
            onDeletePerson={onDeletePerson}
            onEditFormChange={onEditFormChange}
          />
        ))}
      </ul>
    </div>
  );
}
