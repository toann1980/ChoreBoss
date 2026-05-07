import type { PersonRead } from '../types';
import type { PersonEditFormState } from './PeoplePanel';

interface PersonRowProps {
  person: PersonRead;
  isAdmin: boolean;
  isEditing: boolean;
  peopleFormBusy: boolean;
  personEditForm: PersonEditFormState | null;
  onEditPerson: (person: PersonRead) => void;
  onCancelEditPerson: () => void;
  onSavePerson: (personId: number) => void;
  onDeletePerson: (personId: number) => void;
  onEditFormChange: (next: Partial<PersonEditFormState>) => void;
}

export function PersonRow({
  person,
  isAdmin,
  isEditing,
  peopleFormBusy,
  personEditForm,
  onEditPerson,
  onCancelEditPerson,
  onSavePerson,
  onDeletePerson,
  onEditFormChange,
}: PersonRowProps) {
  return (
    <li>
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
}
