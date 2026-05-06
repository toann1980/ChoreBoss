import type { FormEvent } from 'react';

interface LoginPageProps {
  loginName: string;
  pin: string;
  loading: boolean;
  message: string;
  isAlertMessage: boolean;
  onLoginNameChange: (value: string) => void;
  onPinChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function LoginPage({
  loginName,
  pin,
  loading,
  message,
  isAlertMessage,
  onLoginNameChange,
  onPinChange,
  onSubmit,
}: LoginPageProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Sign in</p>
          <h2>Use your login name and PIN</h2>
        </div>
      </div>

      <form className="login-form" onSubmit={onSubmit}>
        <label>
          Login name
          <input
            name="loginName"
            autoComplete="username"
            value={loginName}
            onChange={(event) => onLoginNameChange(event.target.value)}
          />
        </label>

        <label>
          PIN
          <input
            name="pin"
            type="password"
            inputMode="numeric"
            autoComplete="current-password"
            value={pin}
            onChange={(event) => onPinChange(event.target.value)}
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <p className="status" role={isAlertMessage ? 'alert' : undefined}>
        {message}
      </p>
    </section>
  );
}
