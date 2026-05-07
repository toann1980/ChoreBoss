import type { ReactNode } from 'react';
import type { AuthSession } from '../types';

interface AppLayoutProps {
  session: AuthSession | null;
  onLogout: () => void;
  children: ReactNode;
}

export function AppLayout({ session, onLogout, children }: AppLayoutProps) {
  const handleHome = (): void => {
    window.location.assign('/');
  };

  return (
    <main className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">ChoreBoss</p>
          <h1>TypeScript frontend</h1>
          <p className="subhead">FastAPI backend, typed UI, and a clean path away from the Flask bridge.</p>
        </div>
        {session ? (
          <div className="header-actions">
            <button type="button" className="secondary-button" onClick={handleHome}>
              Home
            </button>
            <button type="button" className="secondary-button" onClick={onLogout}>
              Sign out
            </button>
          </div>
        ) : null}
      </header>

      {children}
    </main>
  );
}
