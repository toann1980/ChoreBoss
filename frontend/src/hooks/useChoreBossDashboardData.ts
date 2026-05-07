import { useEffect, useState } from 'react';
import { loadChores, loadPeople } from '../api';
import type { AuthSession, ChoreRead, PersonRead } from '../types';

interface UseChoreBossDashboardDataOptions {
  session: AuthSession | null;
  onMessageChange: (message: string) => void;
}

export interface UseChoreBossDashboardDataResult {
  chores: ChoreRead[];
  people: PersonRead[];
  dashboardLoading: boolean;
  setChores: import('react').Dispatch<import('react').SetStateAction<ChoreRead[]>>;
  setPeople: import('react').Dispatch<import('react').SetStateAction<PersonRead[]>>;
}

export function useChoreBossDashboardData({
  session,
  onMessageChange,
}: UseChoreBossDashboardDataOptions): UseChoreBossDashboardDataResult {
  const [chores, setChores] = useState<ChoreRead[]>([]);
  const [people, setPeople] = useState<PersonRead[]>([]);
  const [dashboardLoading, setDashboardLoading] = useState(false);

  useEffect(() => {
    if (!session) {
      return;
    }

    let isCurrent = true;

    const run = async (): Promise<void> => {
      setDashboardLoading(true);
      onMessageChange('Loading chores…');

      try {
        const [nextChores, nextPeople] = await Promise.all([
          loadChores(session.access_token),
          loadPeople(session.access_token),
        ]);
        if (!isCurrent) {
          return;
        }
        setChores(nextChores);
        setPeople(nextPeople);
        onMessageChange(`Welcome, ${session.loginName}`);
      } catch (error: unknown) {
        if (!isCurrent) {
          return;
        }
        onMessageChange(error instanceof Error ? error.message : 'Failed to load chores');
      } finally {
        if (isCurrent) {
          setDashboardLoading(false);
        }
      }
    };

    void run();

    return () => {
      isCurrent = false;
    };
  }, [session, onMessageChange]);

  return {
    chores,
    people,
    dashboardLoading,
    setChores,
    setPeople,
  };
}
