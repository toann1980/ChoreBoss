# Phase 2 Frontend Planning — CSS Analysis & Best Practices

**Date:** 2026-04-20  
**Purpose:** Analyze existing Flask/Jinja2 CSS, propose React/Tailwind equivalent

---

## Current CSS Analysis (Existing Style)

### Color Palette
- **Background:** White (#ffffff)
- **Accent:** Light gray (#f8f8f8)
- **Text:** Dark gray (#555555)
- **Minimal branding:** Subtle, understated

### Layout Patterns

#### Header (50vh)
```css
header {
    flex-direction: column;
    height: 50vh;
    center-aligned
}
```
- **Observation:** Large hero section
- **Use:** App title, welcome message, branding
- **Height:** 50% of viewport (tall, prominent)

#### Main Content (flexible)
```css
main {
    flex: 1;
    overflow-y: auto;
}
```
- **Observation:** Scrollable content area
- **Flexibility:** Takes remaining vertical space
- **Pattern:** Good for long lists

#### Footer (10vh)
```css
footer {
    height: 10vh;
    background-color: #f8f8f8;
}
```
- **Observation:** Persistent footer
- **Use:** Copyright, links, status
- **Height:** 10% of viewport

### Typography
- **Font:** Arial, sans-serif (system default)
- **H1:** 2rem (32px)
- **H2:** 1.5rem (24px)
- **Body:** 16px (implicit)
- **Style:** Clean, minimal, accessible

### Spacing
- **Button padding:** 1rem × 2rem (generous, touch-friendly)
- **Section margin:** 20px
- **Margin-bottom:** 3rem (sections)
- **Container padding:** 1rem

### Interaction
- **Button size:** Large (good for touch/mobile)
- **Padding:** Generous (1rem top/bottom)
- **No hover effects defined:** Suggests Bootstrap handles it

### Observations

✅ **What's Good:**
1. Simple, clean aesthetic (minimal CSS)
2. Responsive flex layout
3. Touch-friendly button sizes
4. Good vertical rhythm (50vh + flex + 10vh)
5. Subtle color scheme (professional)

⚠️ **What Could Improve:**
1. No responsive breakpoints (mobile needs work)
2. No dark mode support
3. Limited color palette
4. No CSS variables for maintainability
5. Arial font (generic, not modern)
6. Relies heavily on Bootstrap for components

---

## Proposed React + Tailwind Implementation

### Modern Tech Stack

**CSS Framework:** Tailwind CSS v4
- Utility-first (matches existing minimalism)
- Mobile-first responsive design
- Dark mode support built-in
- CSS variables for theming
- Smaller bundle than Bootstrap

**Component Library:** shadcn/ui
- Built on Tailwind + Radix UI
- Professional, accessible components
- Matches modern design patterns
- Zero-dependency (imports, not npm)
- Perfect for household apps (cards, forms, modals)

**State Management:** Zustand
- Lightweight (lightweight like the CSS!)
- Perfect for household chores app (small state)
- Local storage support built-in
- Minimal boilerplate

**Data Fetching:** React Query (TanStack Query)
- Handles async API calls
- Caching, background sync
- Loading/error states
- Real-time updates ready

---

## Design System Proposal

### Color Palette (Expanded)

```tailwind
Primary:    blue-600   (action, primary buttons, links)
Secondary:  slate-500  (muted text, secondary actions)
Success:    green-600  (completed chores, confirmations)
Warning:    amber-500  (overdue, attention)
Danger:     red-600    (delete, errors)
Background: white      (light mode) / slate-950 (dark)
Surface:    slate-50   (light mode) / slate-900 (dark)
Border:     slate-200  (light mode) / slate-700 (dark)
Text:       slate-900  (light mode) / slate-50 (dark)
```

### Typography Scale

```
H1:  text-4xl  font-bold    (page titles)
H2:  text-2xl  font-bold    (section titles)
H3:  text-xl   font-semibold (subsections)
Body: text-base font-normal (paragraphs)
Small: text-sm font-normal  (labels, captions)
Tiny:  text-xs font-normal  (hints)
```

**Font Stack:**
```css
font-family: "Inter", "Segoe UI", sans-serif;
```
Modern, clean, excellent readability.

### Spacing Scale (Tailwind default)

```
xs: 4px     (tiny gaps)
sm: 8px     (small gaps)
md: 16px    (default)
lg: 24px    (sections)
xl: 32px    (large sections)
2xl: 48px   (hero)
```

### Component Sizing

**Buttons:**
- Small: `px-3 py-1.5 text-sm` (minimal actions)
- Default: `px-4 py-2 text-base` (standard)
- Large: `px-6 py-3 text-lg` (primary, touch-friendly)

**Cards:**
- Padding: `p-4` or `p-6`
- Border: `border border-slate-200 rounded-lg`
- Shadow: `shadow-sm` or `shadow-md`

**Forms:**
- Label: `block text-sm font-medium mb-2`
- Input: `w-full px-3 py-2 border rounded-md focus:ring-2`
- Error: `text-red-600 text-sm mt-1`

---

## Layout Patterns

### Header → Content → Footer (Keep Existing!)

```tsx
export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Hero Header */}
      <header className="flex flex-col justify-center items-center h-1/2 bg-gradient-to-br from-blue-50 to-slate-50 flex-shrink-0">
        <h1 className="text-4xl font-bold text-slate-900">🏠 ChoreBoss</h1>
        <p className="text-lg text-slate-600 mt-2">Family chores made easy</p>
      </header>

      {/* Scrollable Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-4">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-50 border-t border-slate-200 h-16 flex justify-center items-center text-sm text-slate-600 flex-shrink-0">
        <p>© 2026 ChoreBoss. Keep your house running smoothly.</p>
      </footer>
    </div>
  );
}
```

### Chores List Component

```tsx
export function ChoresList({ chores }: { chores: Chore[] }) {
  return (
    <div className="space-y-4">
      {chores.map((chore) => (
        <Card key={chore.id} className="p-4 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-slate-900">
                {chore.name}
              </h3>
              <p className="text-slate-600 text-sm mt-1">
                {chore.description}
              </p>
              {chore.person && (
                <p className="text-xs text-slate-500 mt-2">
                  Assigned to: <span className="font-medium">{chore.person.first_name}</span>
                </p>
              )}
            </div>
            <Button
              onClick={() => completeChore(chore.id)}
              className="bg-green-600 hover:bg-green-700"
            >
              ✓ Done
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}
```

### Login Page (PIN Pad)

```tsx
export function LoginPage() {
  const [personId, setPersonId] = useState("");
  const [pin, setPin] = useState("");

  const handlePin = (digit: string) => {
    if (pin.length < 4) {
      setPin(pin + digit);
    }
  };

  return (
    <div className="flex flex-col h-screen justify-center items-center bg-gradient-to-br from-blue-50 to-slate-50">
      <Card className="w-full max-w-sm p-8">
        <h1 className="text-3xl font-bold text-center mb-8">🏠 ChoreBoss</h1>

        {/* Person ID Select */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Who are you?
          </label>
          <select
            value={personId}
            onChange={(e) => setPersonId(e.target.value)}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select person...</option>
            {people.map((p) => (
              <option key={p.id} value={p.id}>
                {p.first_name} {p.last_name}
              </option>
            ))}
          </select>
        </div>

        {/* PIN Pad */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Enter PIN
          </label>
          <input
            type="password"
            value={pin}
            readOnly
            className="w-full px-4 py-3 text-center text-2xl border border-slate-300 rounded-lg tracking-widest"
          />
        </div>

        {/* Numeric Keypad */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((digit) => (
            <Button
              key={digit}
              onClick={() => handlePin(String(digit))}
              className="h-12 text-lg font-semibold"
            >
              {digit}
            </Button>
          ))}
          <Button
            onClick={() => handlePin("0")}
            className="col-span-2 h-12 text-lg font-semibold"
          >
            0
          </Button>
          <Button
            onClick={() => setPin(pin.slice(0, -1))}
            className="h-12 bg-slate-400 hover:bg-slate-500"
          >
            ← Delete
          </Button>
        </div>

        <Button
          onClick={handleLogin}
          disabled={!personId || pin.length !== 4}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          Login
        </Button>
      </Card>
    </div>
  );
}
```

---

## Dark Mode Support

Tailwind makes dark mode trivial:

```tsx
{/* Automatically switches with system preference */}
<div className="bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50">
  {/* Content */}
</div>
```

---

## Responsive Design Strategy

### Mobile-First (Tailwind default)

```tsx
<div className="flex flex-col md:flex-row gap-4">
  {/* Mobile: stacked (flex-col) */}
  {/* Desktop: side-by-side (md:flex-row) */}
</div>
```

### Breakpoints to Use

- `sm`: 640px (small phones, landscape)
- `md`: 768px (tablets)
- `lg`: 1024px (laptops)
- `xl`: 1280px (desktops)

### Example: Responsive Dashboard

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {chores.map((chore) => (
    <ChoreCard key={chore.id} chore={chore} />
  ))}
</div>
```

---

## Best Practices Summary

### ✅ DO

1. **Use Tailwind utilities** — no custom CSS needed
2. **Extract components** — reusable React components for common patterns
3. **Use shadcn/ui components** — Card, Button, Modal, Form, etc.
4. **Responsive-first** — mobile design, then enhance for desktop
5. **Dark mode support** — built into Tailwind, minimal effort
6. **Semantic HTML** — use `<form>`, `<input>`, `<button>`, etc.
7. **Accessibility** — ARIA labels, focus states, keyboard nav
8. **Test interactions** — Jest + React Testing Library for components

### ❌ DON'T

1. **Don't write CSS** — use Tailwind utilities instead
2. **Don't hardcode colors** — use Tailwind's color palette
3. **Don't ignore mobile** — mobile-first is the standard now
4. **Don't skip accessibility** — WCAG 2.1 AA is the target
5. **Don't over-complicate** — keep components simple and focused

---

## File Structure (Proposed)

```
frontend/
├── src/
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ChoresPage.tsx
│   │   └── PeoplePage.tsx
│   ├── components/
│   │   ├── AppLayout.tsx
│   │   ├── ChoreCard.tsx
│   │   ├── ChoresList.tsx
│   │   ├── PersonCard.tsx
│   │   ├── LoginForm.tsx
│   │   └── PinPad.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useChores.ts
│   │   └── usePeople.ts
│   ├── store/
│   │   └── authStore.ts
│   ├── api/
│   │   └── client.ts
│   ├── styles/
│   │   └── globals.css
│   └── App.tsx
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Migration Path (Flask → React)

### Phase 2a: Setup (1-2 hours)
1. `npm create vite@latest frontend -- --template react-ts`
2. Install Tailwind, shadcn/ui, Zustand, React Query
3. Configure TypeScript, ESLint, Prettier
4. Setup API client

### Phase 2b: Core Pages (4-6 hours)
1. Build AppLayout + basic routing
2. Build LoginPage with PIN pad
3. Build DashboardPage (main view)
4. Build ChoresPage + People Page

### Phase 2c: Integration (2-3 hours)
1. Connect to FastAPI backend
2. Test all endpoints
3. Error handling, loading states
4. Dark mode toggle

### Phase 2d: Polish (1-2 hours)
1. Mobile responsiveness
2. Accessibility audit
3. Performance optimization
4. Deployment setup

---

## Tools to Install (Phase 2)

```bash
npm install react react-dom
npm install -D tailwindcss postcss autoprefixer
npm install -D typescript @types/react @types/react-dom
npm install zustand @tanstack/react-query
npm install axios  # or fetch wrapper
npm install lucide-react  # icons
npm install -D shadcn-ui

# Optional
npm install -D jest @testing-library/react
npm install -D prettier eslint
```

---

## Summary

**Existing Design:** Clean, minimal, touch-friendly  
**New Direction:** Same principles, modern tools  

**Tailwind + shadcn/ui will:**
- ✅ Keep the clean aesthetic
- ✅ Add responsive design
- ✅ Support dark mode
- ✅ Reduce CSS complexity
- ✅ Improve accessibility
- ✅ Enable faster development

**Ready for Phase 2! 🚀**
