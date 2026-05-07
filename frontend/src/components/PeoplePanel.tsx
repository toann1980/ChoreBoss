import type { FormEvent } from 'react';
import { PersonRow } from './PersonRow';
import type { PersonRead } from '../types';

export interface PersonCreateFormState {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  pin: string;
  is_admin: boolean;
}

export interface PersonEditFormState {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  is_admin: boolean;
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
        <form className="people-form" onSubmit={onCreatePerson}>
          <h4>Add person</h4>
          <div className="people-form-grid">
            <label>
              First name
              <input
                name="first_name"
                value={personCreateForm.first_name}
                onChange={(event) => onCreateFormChange({ first_name: event.target.value })}
              />
            </label>
            <label>
              Last name
              <input
                name="last_name"
                value={personCreateForm.last_name}
                onChange={(event) => onCreateFormChange({ last_name: event.target.value })}
              />
            </label>
            <label>
              Login name
              <input
                name="login_name"
                value={personCreateForm.login_name}
                onChange={(event) => onCreateFormChange({ login_name: event.target.value })}
              />
            </label>
            <label>
              Birthday
              <input
                name="birthday"
                type="date"
                value={personCreateForm.birthday}
                onChange={(event) => onCreateFormChange({ birthday: event.target.value })}
              />
            </label>
            <label>
              PIN
              <input
                name="pin"
                type="password"
                inputMode="numeric"
                value={personCreateForm.pin}
                onChange={(event) => onCreateFormChange({ pin: event.target.value })}
              />
            </label>
            <label className="checkbox-row">
              <input
                name="is_admin"
                type="checkbox"
                checked={personCreateForm.is_admin}
                onChange={(event) => onCreateFormChange({ is_admin: event.target.checked })}
              />
              Admin
            </label>
          </div>
          <button type="submit" disabled={peopleFormBusy}>
            {peopleFormBusy ? 'Saving…' : 'Add person'}
          </button>
        </form>
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
