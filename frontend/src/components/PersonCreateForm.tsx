import type { FormEvent } from 'react';
import type { PersonCreateFormState } from './PeoplePanel';

interface PersonCreateFormProps {
  busy: boolean;
  form: PersonCreateFormState;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onChange: (next: Partial<PersonCreateFormState>) => void;
}

export function PersonCreateForm({ busy, form, onSubmit, onChange }: PersonCreateFormProps) {
  return (
    <form className="people-form" onSubmit={onSubmit}>
      <h4>Add person</h4>
      <div className="people-form-grid">
        <label>
          First name
          <input
            name="first_name"
            value={form.first_name}
            onChange={(event) => onChange({ first_name: event.target.value })}
          />
        </label>
        <label>
          Last name
          <input
            name="last_name"
            value={form.last_name}
            onChange={(event) => onChange({ last_name: event.target.value })}
          />
        </label>
        <label>
          Login name
          <input
            name="login_name"
            value={form.login_name}
            onChange={(event) => onChange({ login_name: event.target.value })}
          />
        </label>
        <label>
          Birthday
          <input
            name="birthday"
            type="date"
            value={form.birthday}
            onChange={(event) => onChange({ birthday: event.target.value })}
          />
        </label>
        <label>
          PIN
          <input
            name="pin"
            type="password"
            inputMode="numeric"
            value={form.pin}
            onChange={(event) => onChange({ pin: event.target.value })}
          />
        </label>
        <label className="checkbox-row">
          <input
            name="is_admin"
            type="checkbox"
            checked={form.is_admin}
            onChange={(event) => onChange({ is_admin: event.target.checked })}
          />
          Admin
        </label>
      </div>
      <button type="submit" disabled={busy}>
        {busy ? 'Saving…' : 'Add person'}
      </button>
    </form>
  );
}
