import type { FormEvent } from 'react';
import { ChoreList } from '../components/ChoreList';
import type { PersonRead } from '../types';

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

function peopleCountLabel(count: number): string {
  return count === 1 ? '1 person' : `${count} people`;
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
      {peopleFormError ? (
        <p className="status" role="alert">
          {peopleFormError}
        </p>
      ) : null}

      <ChoreList
        chores={chores}
        dashboardLoading={dashboardLoading}
        completingChoreId={completingChoreId}
        onCompleteChore={onCompleteChore}
      />

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
                          onChange={(event) => onEditFormChange({ first_name: event.target.value })}
                        />
                      </label>
                      <label>
                        Last name
                        <input
                          value={personEditForm.last_name}
                          onChange={(event) => onEditFormChange({ last_name: event.target.value })}
                        />
                      </label>
                      <label>
                        Login name
                        <input
                          value={personEditForm.login_name}
                          onChange={(event) => onEditFormChange({ login_name: event.target.value })}
                        />
                      </label>
                      <label>
                        Birthday
                        <input
                          type="date"
                          value={personEditForm.birthday}
                          onChange={(event) => onEditFormChange({ birthday: event.target.value })}
                        />
                      </label>
                      <label className="checkbox-row">
                        <input
                          type="checkbox"
                          checked={personEditForm.is_admin}
                          onChange={(event) => onEditFormChange({ is_admin: event.target.checked })}
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
                          onSavePerson(person.id);
                        }}
                      >
                        {peopleFormBusy ? 'Saving…' : 'Save'}
                      </button>
                      <button
                        type="button"
                        className="secondary-button"
                        disabled={peopleFormBusy}
                        onClick={onCancelEditPerson}
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
                    {isAdmin ? (
                      <div className="people-actions">
                        <button type="button" className="secondary-button" onClick={() => onEditPerson(person)}>
                          Edit
                        </button>
                        <button
                          type="button"
                          className="secondary-button"
                          disabled={peopleFormBusy}
                          onClick={() => {
                            onDeletePerson(person.id);
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
  );
}
