import type { ChoreRead } from '../types';

interface ChoreListProps {
  chores: ChoreRead[];
  dashboardLoading: boolean;
  completingChoreId: number | null;
  onCompleteChore: (choreId: number) => void;
}

export function ChoreList({ chores, dashboardLoading, completingChoreId, onCompleteChore }: ChoreListProps) {
  return (
    <div className="list-card">
      <div className="list-card-header">
        <h3>Chores</h3>
        {dashboardLoading ? <span>Loading…</span> : <span>{chores.length} items</span>}
      </div>
      <ul className="chore-list">
        {chores.map((chore) => (
          <li key={chore.id}>
            <strong>{chore.name}</strong>
            <p>{chore.description}</p>
            <button
              type="button"
              className="secondary-button chore-action"
              disabled={completingChoreId === chore.id}
              onClick={() => {
                onCompleteChore(chore.id);
              }}
            >
              {completingChoreId === chore.id ? 'Completing…' : 'Mark complete'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
