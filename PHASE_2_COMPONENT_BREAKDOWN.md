# Phase 2 Frontend Conversion — Component Breakdown & Proposal

**Date:** 2026-04-20  
**Purpose:** Map Flask routes → React components, propose reusable component library

---

## API Endpoint Analysis

### Current API Endpoints (FastAPI)

```
POST   /api/auth/login              ← Authentication
GET    /api/health                  ← Health check

GET    /api/chores/                 ← List all chores
GET    /api/chores/{id}             ← Get single chore
POST   /api/chores/                 ← Create (admin only)
PUT    /api/chores/{id}             ← Update (admin only)
DELETE /api/chores/{id}             ← Delete (admin only)
POST   /api/chores/{id}/complete    ← Mark complete + auto-assign

GET    /api/people/                 ← List all people
GET    /api/people/{id}             ← Get single person
POST   /api/people/                 ← Create (admin only)
PUT    /api/people/{id}             ← Update (admin only)
DELETE /api/people/{id}             ← Delete (admin only)
```

### Response Format (Example)

```json
// GET /api/chores/ → Returns array directly
[
  {
    "id": 1,
    "name": "Wash dishes",
    "description": "Wash all dishes",
    "person_id": 1,
    "person": {
      "id": 1,
      "first_name": "Alice",
      "last_name": "Smith"
    },
    "last_completed_date": "2026-04-20T12:00:00",
    "last_completed_id": 1,
    "created_at": "2026-04-20T12:00:00",
    "updated_at": "2026-04-20T12:00:00"
  }
]

// POST /api/auth/login → Returns token
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "person_id": 1,
  "is_admin": true
}
```

---

## Current Flask Routes → React Components Mapping

| Flask Route | Method | Purpose | React Component |
|-------------|--------|---------|-----------------|
| `/login` | GET/POST | PIN authentication | `LoginPage` |
| `/` | GET | Dashboard | `DashboardPage` |
| `/chores` | GET | List chores | `ChoresPage` |
| `/chores/<id>` | GET | View chore | `ChoreDetailPage` |
| `/chores/add` | GET/POST | Create chore | `ChoreFormModal` |
| `/chores/<id>/edit` | GET/POST | Edit chore | `ChoreFormModal` |
| `/chores/<id>/complete` | POST | Mark complete | `ChoreCard` action |
| `/chores/<id>/delete` | POST | Delete chore | `ChoreCard` action |
| `/people` | GET | List people | `PeoplePage` |
| `/people/<id>` | GET | View person | `PersonDetailPage` |
| `/people/add` | GET/POST | Create person | `PersonFormModal` |
| `/logout` | GET | Clear session | Navigation action |

---

## Proposed Component Architecture

### Layout Components (Shared)

#### 1. **AppLayout** (Wrapper)
```tsx
export function AppLayout({ children, showHeader = true }: Props) {
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {showHeader && <Header />}
      <main className="flex-1 overflow-y-auto bg-gradient-to-br from-slate-50 to-white">
        <div className="max-w-6xl mx-auto px-4 py-6">
          {children}
        </div>
      </main>
      <Footer />
    </div>
  );
}
```

**Usage:** Wraps every page, provides consistent layout  
**Props:** `children`, `showHeader`, `title`, `subtitle`

#### 2. **Header** (Hero Section)
```tsx
export function Header() {
  const { user } = useAuth();
  
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold flex items-center gap-2">
          🏠 ChoreBoss
        </h1>
        {user && (
          <p className="text-blue-100 mt-2">
            Welcome back, {user.first_name}!
          </p>
        )}
      </div>
    </header>
  );
}
```

**Usage:** Every page top  
**Features:** Dynamic greeting, responsive sizing

#### 3. **Footer** (Static)
```tsx
export function Footer() {
  return (
    <footer className="bg-slate-50 border-t border-slate-200 py-4 px-4 text-center text-sm text-slate-600">
      <p>© 2026 ChoreBoss. Keep your house running smoothly. 🏠</p>
    </footer>
  );
}
```

---

### Page Components

#### 4. **LoginPage** (Authentication)
```tsx
export function LoginPage() {
  const [personId, setPersonId] = useState("");
  const [pin, setPin] = useState("");
  const [people, setPeople] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { setToken } = useAuth();

  useEffect(() => {
    // Fetch list of people for dropdown
    fetchPeople();
  }, []);

  const handlePinDigit = (digit: string) => {
    if (pin.length < 4) setPin(pin + digit);
  };

  const handleLogin = async () => {
    try {
      const response = await api.post('/auth/login', {
        person_id: parseInt(personId),
        pin
      });
      setToken(response.data.access_token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-slate-50 px-4">
      <Card className="w-full max-w-sm">
        <div className="space-y-6 p-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold">🏠</h1>
            <h2 className="text-2xl font-bold mt-2">ChoreBoss</h2>
          </div>

          {error && <Alert variant="destructive">{error}</Alert>}

          {/* Person Selector */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Who are you?
            </label>
            <select
              value={personId}
              onChange={(e) => setPersonId(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select person...</option>
              {people.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.first_name} {p.last_name}
                </option>
              ))}
            </select>
          </div>

          {/* PIN Display */}
          <div>
            <label className="block text-sm font-medium mb-2">Enter PIN</label>
            <input
              type="password"
              value={pin}
              readOnly
              className="w-full px-4 py-4 text-center text-3xl tracking-widest border-2 border-slate-300 rounded-lg font-mono"
            />
          </div>

          {/* PIN Pad */}
          <PinPad
            onDigit={handlePinDigit}
            onBackspace={() => setPin(pin.slice(0, -1))}
            onSubmit={handleLogin}
            disabled={!personId || pin.length !== 4}
          />
        </div>
      </Card>
    </div>
  );
}
```

**Props:** None (uses context/hooks)  
**State:** `personId`, `pin`, `people`, `error`  
**Features:**
- Person dropdown (fetched from API)
- PIN entry with keypad
- Visual feedback
- Error display

#### 5. **DashboardPage** (Home)
```tsx
export function DashboardPage() {
  const { user } = useAuth();
  const { data: chores, isLoading } = useChores();
  const { data: people } = usePeople();

  const assignedToMe = chores?.filter(c => c.person_id === user?.id) || [];
  const overdue = assignedToMe.filter(c => !c.last_completed_date);

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            title="My Chores"
            value={assignedToMe.length}
            icon="📋"
            color="blue"
          />
          <StatCard
            title="Overdue"
            value={overdue.length}
            icon="⚠️"
            color={overdue.length > 0 ? "red" : "green"}
          />
          <StatCard
            title="Team Members"
            value={people?.length || 0}
            icon="👥"
            color="purple"
          />
        </div>

        {/* My Chores Section */}
        <section>
          <h2 className="text-2xl font-bold mb-4">My Chores</h2>
          {isLoading ? (
            <LoadingSpinner />
          ) : assignedToMe.length > 0 ? (
            <div className="space-y-3">
              {assignedToMe.map((chore) => (
                <ChoreCard
                  key={chore.id}
                  chore={chore}
                  onComplete={() => completeChore(chore.id)}
                  onEdit={() => navigate(`/chores/${chore.id}/edit`)}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              icon="✨"
              title="No chores assigned"
              subtitle="You're all caught up!"
            />
          )}
        </section>

        {/* Recent Completions */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Recently Completed</h2>
          <RecentCompletionsList chores={chores} limit={5} />
        </section>
      </div>
    </AppLayout>
  );
}
```

**Props:** None  
**Dependencies:** `useChores()`, `usePeople()`, `useAuth()`  
**Components Used:** `StatCard`, `ChoreCard`, `LoadingSpinner`, `EmptyState`

#### 6. **ChoresPage** (List View)
```tsx
export function ChoresPage() {
  const { data: chores, isLoading } = useChores();
  const { user } = useAuth();
  const [filter, setFilter] = useState<"all" | "assigned" | "unassigned">("all");

  const filtered = chores?.filter((c) => {
    if (filter === "assigned") return c.person_id;
    if (filter === "unassigned") return !c.person_id;
    return true;
  });

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-3xl font-bold">All Chores</h2>
          {user?.is_admin && (
            <Button
              onClick={() => navigate('/chores/add')}
              className="bg-blue-600 hover:bg-blue-700"
            >
              + Add Chore
            </Button>
          )}
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          {["all", "assigned", "unassigned"].map((f) => (
            <Button
              key={f}
              variant={filter === f ? "default" : "outline"}
              onClick={() => setFilter(f as any)}
              className="capitalize"
            >
              {f}
            </Button>
          ))}
        </div>

        {/* Chores List */}
        {isLoading ? (
          <LoadingSpinner />
        ) : filtered?.length ? (
          <div className="space-y-3">
            {filtered.map((chore) => (
              <ChoreCard
                key={chore.id}
                chore={chore}
                expanded
                onComplete={() => completeChore(chore.id)}
                onEdit={() => user?.is_admin && navigate(`/chores/${chore.id}/edit`)}
                onDelete={() => user?.is_admin && deleteChore(chore.id)}
              />
            ))}
          </div>
        ) : (
          <EmptyState icon="✨" title="No chores found" />
        )}
      </div>
    </AppLayout>
  );
}
```

---

### Reusable UI Components (shadcn/ui Base)

#### 7. **ChoreCard** (Flexible Container)
```tsx
interface ChoreCardProps {
  chore: Chore;
  expanded?: boolean;
  onComplete?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

export function ChoreCard({
  chore,
  expanded = false,
  onComplete,
  onEdit,
  onDelete,
}: ChoreCardProps) {
  const [isCompleting, setIsCompleting] = useState(false);

  const handleComplete = async () => {
    setIsCompleting(true);
    try {
      await onComplete?.();
    } finally {
      setIsCompleting(false);
    }
  };

  const statusColor = chore.last_completed_date
    ? "bg-green-50 border-green-200"
    : "bg-amber-50 border-amber-200";

  return (
    <Card className={`p-4 border-2 ${statusColor} hover:shadow-md transition-shadow`}>
      <div className="flex justify-between items-start">
        <div className="flex-1 space-y-1">
          <h3 className="font-semibold text-lg text-slate-900">
            {chore.name}
          </h3>
          <p className="text-slate-600 text-sm">{chore.description}</p>

          {expanded && (
            <div className="mt-3 pt-3 border-t border-slate-200 space-y-2 text-xs text-slate-500">
              {chore.person && (
                <div>
                  <span className="font-medium">Assigned to:</span>{" "}
                  {chore.person.first_name} {chore.person.last_name}
                </div>
              )}
              {chore.last_completed_date && (
                <div>
                  <span className="font-medium">Last completed:</span>{" "}
                  {formatDate(chore.last_completed_date)} by{" "}
                  {chore.last_completed?.first_name}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex gap-2 ml-4">
          {onComplete && (
            <Button
              onClick={handleComplete}
              disabled={isCompleting}
              className="bg-green-600 hover:bg-green-700 text-white"
              size="sm"
            >
              {isCompleting ? "✓ Marking..." : "✓ Done"}
            </Button>
          )}
          {onEdit && (
            <Button onClick={onEdit} variant="outline" size="sm">
              ✎ Edit
            </Button>
          )}
          {onDelete && (
            <Button
              onClick={onDelete}
              variant="destructive"
              size="sm"
              className="hidden md:flex"
            >
              🗑 Delete
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
```

**Props:** `chore`, `expanded`, callbacks  
**States:** `isCompleting`, loading  
**Features:**
- Compact and expanded modes
- Status-based styling
- Responsive button layout
- Optimistic updates

#### 8. **PinPad** (Custom Input)
```tsx
interface PinPadProps {
  onDigit: (digit: string) => void;
  onBackspace: () => void;
  onSubmit: () => void;
  disabled?: boolean;
}

export function PinPad({
  onDigit,
  onBackspace,
  onSubmit,
  disabled = false,
}: PinPadProps) {
  return (
    <div className="space-y-4">
      {/* Numeric Keypad */}
      <div className="grid grid-cols-3 gap-2">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((digit) => (
          <Button
            key={digit}
            onClick={() => onDigit(String(digit))}
            disabled={disabled}
            className="h-14 text-xl font-semibold bg-slate-100 hover:bg-slate-200 text-slate-900"
          >
            {digit}
          </Button>
        ))}

        {/* 0 Button (span 2 cols) */}
        <Button
          onClick={() => onDigit("0")}
          disabled={disabled}
          className="col-span-2 h-14 text-xl font-semibold bg-slate-100 hover:bg-slate-200 text-slate-900"
        >
          0
        </Button>

        {/* Backspace */}
        <Button
          onClick={onBackspace}
          disabled={disabled}
          className="h-14 bg-slate-400 hover:bg-slate-500 text-white"
        >
          ← Back
        </Button>
      </div>

      {/* Submit Button */}
      <Button
        onClick={onSubmit}
        disabled={disabled}
        className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-lg"
      >
        Login
      </Button>
    </div>
  );
}
```

**Standalone component** - reusable for any PIN entry  
**Features:** Numeric layout, backspace, submit

#### 9. **StatCard** (Dashboard Metric)
```tsx
interface StatCardProps {
  title: string;
  value: number | string;
  icon?: string;
  color?: "blue" | "red" | "green" | "purple";
  onClick?: () => void;
}

export function StatCard({
  title,
  value,
  icon,
  color = "blue",
  onClick,
}: StatCardProps) {
  const bgColor = {
    blue: "bg-blue-50 border-blue-200",
    red: "bg-red-50 border-red-200",
    green: "bg-green-50 border-green-200",
    purple: "bg-purple-50 border-purple-200",
  }[color];

  const textColor = {
    blue: "text-blue-600",
    red: "text-red-600",
    green: "text-green-600",
    purple: "text-purple-600",
  }[color];

  return (
    <Card
      className={`p-6 border-2 ${bgColor} cursor-pointer hover:shadow-md transition-all`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-600 font-medium">{title}</p>
          <p className={`text-3xl font-bold ${textColor}`}>{value}</p>
        </div>
        {icon && <span className="text-4xl">{icon}</span>}
      </div>
    </Card>
  );
}
```

#### 10. **EmptyState** (Fallback UI)
```tsx
interface EmptyStateProps {
  icon: string;
  title: string;
  subtitle?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({
  icon,
  title,
  subtitle,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <span className="text-6xl mb-4">{icon}</span>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      {subtitle && <p className="text-slate-600 mb-6">{subtitle}</p>}
      {action && (
        <Button onClick={action.onClick} className="mt-4">
          {action.label}
        </Button>
      )}
    </div>
  );
}
```

#### 11. **LoadingSpinner** (Feedback)
```tsx
export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-200 border-t-blue-600"></div>
    </div>
  );
}
```

---

## Custom Hooks (Data Layer)

#### 12. **useAuth** (Context)
```tsx
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}

// Usage:
const { user, token, setToken, logout } = useAuth();
```

#### 13. **useChores** (Data Fetching)
```tsx
export function useChores() {
  const { token } = useAuth();
  const query = useQuery({
    queryKey: ["chores"],
    queryFn: async () => {
      const response = await api.get("/chores/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
    staleTime: 30000, // 30 seconds
  });
  return query;
}
```

#### 14. **usePeople** (Data Fetching)
```tsx
export function usePeople() {
  const { token } = useAuth();
  const query = useQuery({
    queryKey: ["people"],
    queryFn: async () => {
      const response = await api.get("/people/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
  });
  return query;
}
```

---

## Component Hierarchy

```
App
├── Router
│   ├── LoginPage (no auth required)
│   └── AppLayout (auth required)
│       ├── Header
│       ├── Page Component
│       │   ├── DashboardPage
│       │   │   ├── StatCard (3x)
│       │   │   └── ChoreCard (multiple)
│       │   ├── ChoresPage
│       │   │   ├── Filters (button group)
│       │   │   └── ChoreCard (multiple)
│       │   ├── PeoplePage
│       │   │   └── PersonCard (multiple)
│       │   └── ChoreFormModal
│       │       └── Form inputs
│       └── Footer
```

---

## File Structure (Phase 2)

```
frontend/
├── src/
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ChoresPage.tsx
│   │   ├── ChoreDetailPage.tsx
│   │   ├── PeoplePage.tsx
│   │   └── PersonDetailPage.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Footer.tsx
│   │   ├── chores/
│   │   │   ├── ChoreCard.tsx
│   │   │   ├── ChoreForm.tsx
│   │   │   └── ChoresList.tsx
│   │   ├── people/
│   │   │   ├── PersonCard.tsx
│   │   │   ├── PersonForm.tsx
│   │   │   └── PeopleList.tsx
│   │   ├── common/
│   │   │   ├── PinPad.tsx
│   │   │   ├── StatCard.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   └── ui/ (shadcn/ui imports)
│   │       ├── card.tsx
│   │       ├── button.tsx
│   │       ├── alert.tsx
│   │       └── ...
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useChores.ts
│   │   ├── usePeople.ts
│   │   └── useMutation.ts
│   ├── store/
│   │   └── authStore.ts (Zustand)
│   ├── api/
│   │   └── client.ts
│   ├── types/
│   │   ├── api.ts
│   │   └── models.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── validators.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
│   ├── images/
│   └── fonts/
└── config files (tailwind, vite, tsconfig, etc.)
```

---

## Summary

**14 Components Proposed:**

### Layout (3)
1. `AppLayout` — Page wrapper
2. `Header` — Hero section
3. `Footer` — Static footer

### Pages (6)
4. `LoginPage` — Authentication
5. `DashboardPage` — Home/summary
6. `ChoresPage` — Chores list
7. `ChoresDetailPage` — Single chore
8. `PeoplePage` — People list
9. `PersonDetailPage` — Single person

### Reusable UI (5)
10. `ChoreCard` — Chore display (compact/expanded)
11. `PinPad` — PIN entry
12. `StatCard` — Dashboard metric
13. `EmptyState` — Fallback UI
14. `LoadingSpinner` — Loading feedback

### Custom Hooks (3+)
- `useAuth()` — User context
- `useChores()` — Fetch chores
- `usePeople()` — Fetch people
- Custom mutation hooks for CRUD

**All type-safe, fully documented, ready for implementation!**
