import { useCallback, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { ApiError, login, toSession } from '../api';
import type { AuthSession } from '../types';

const STORAGE_KEY = 'choreboss.session';

interface LoginFormState {
  loginName: string;
  pin: string;
}

interface UseChoreBossAuthOptions {
  onMessageChange: (message: string) => void;
  onLogoutCleanup: () => void;
}

export interface UseChoreBossAuthResult {
  session: AuthSession | null;
  loginForm: LoginFormState;
  loading: boolean;
  isAuthenticated: boolean;
  handleLogin: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleLogout: () => void;
  setLoginName: (value: string) => void;
  setPin: (value: string) => void;
}

function readSession(): AuthSession | null {
  const rawSession = window.localStorage.getItem(STORAGE_KEY);
  if (!rawSession) {
    return null;
  }

  try {
    return JSON.parse(rawSession) as AuthSession;
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function useChoreBossAuth({ onMessageChange, onLogoutCleanup }: UseChoreBossAuthOptions): UseChoreBossAuthResult {
  const [session, setSession] = useState<AuthSession | null>(() => readSession());
  const [loginForm, setLoginForm] = useState<LoginFormState>({
    loginName: '',
    pin: '',
  });
  const [loading, setLoading] = useState(false);

  const isAuthenticated = useMemo(() => session !== null, [session]);

  const handleLogin = useCallback(async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    setLoading(true);
    onMessageChange('');

    try {
      const loginResponse = await login(loginForm.loginName, loginForm.pin);
      const nextSession = toSession(loginForm.loginName, loginResponse);
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
      setSession(nextSession);
    } catch (error: unknown) {
      const text = error instanceof ApiError ? error.message : 'Unable to sign in';
      onMessageChange(text);
    } finally {
      setLoading(false);
    }
  }, [loginForm.loginName, loginForm.pin, onMessageChange]);

  const handleLogout = useCallback((): void => {
    window.localStorage.removeItem(STORAGE_KEY);
    setSession(null);
    setLoginForm({ loginName: '', pin: '' });
    onMessageChange('Signed out');
    onLogoutCleanup();
  }, [onLogoutCleanup, onMessageChange]);

  return {
    session,
    loginForm,
    loading,
    isAuthenticated,
    handleLogin,
    handleLogout,
    setLoginName: (value) => {
      setLoginForm((current) => ({ ...current, loginName: value }));
    },
    setPin: (value) => {
      setLoginForm((current) => ({ ...current, pin: value }));
    },
  };
}
