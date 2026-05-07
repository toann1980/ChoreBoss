import { useState } from 'react';
import { completeChore } from '../api';
import type { AuthSession, ChoreRead } from '../types';

interface UseChoreBossChoreCompletionOptions {
  session: AuthSession | null;
  setChores: import('react').Dispatch<import('react').SetStateAction<ChoreRead[]>>;
  onMessageChange: (message: string) => void;
}

export interface UseChoreBossChoreCompletionResult {
  completingChoreId: number | null;
  completeChoreById: (choreId: number) => void;
}

export function useChoreBossChoreCompletion({
  session,
  setChores,
  onMessageChange,
}: UseChoreBossChoreCompletionOptions): UseChoreBossChoreCompletionResult {
  const [completingChoreId, setCompletingChoreId] = useState<number | null>(null);

  async function handleCompleteChore(choreId: number): Promise<void> {
    if (!session) {
      return;
    }

    setCompletingChoreId(choreId);
    try {
      const updatedChore = await completeChore(session.access_token, choreId);
      setChores((current) => current.map((chore) => (chore.id === updatedChore.id ? updatedChore : chore)));
      onMessageChange(`Completed ${updatedChore.name}`);
    } catch (error: unknown) {
      onMessageChange(error instanceof Error ? error.message : 'Unable to complete chore');
    } finally {
      setCompletingChoreId(null);
    }
  }

  return {
    completingChoreId,
    completeChoreById: (choreId) => {
      void handleCompleteChore(choreId);
    },
  };
}
