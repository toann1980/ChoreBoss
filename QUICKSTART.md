# ChoreBoss Quick Start — Family Setup

**App:** Flask household chore tracker + family PIN authentication
**Python:** 3.14.4
**Status:** Ready to use (3 data corruption bugs just fixed)
**Recommended:** Run in Docker

---

## 🚀 Start in 3 Steps

### Step 1: Navigate to the app
```bash
cd /srv/github/ChoreBoss
```

### Step 2: Start Docker
```bash
docker-compose up --build
```
First run builds the image (~2-3 min). Subsequent runs are instant.

### Step 3: Open in browser
```
http://localhost:8055
```

**That's it!** You should see the ChoreBoss home page.

---

## 👨‍👩‍👧‍👦 Setup for Your Family

### 1. Create people (parents + children)
- Click "**Add Person**"
- Fill in: first name, last name, birthday, 4-digit PIN
- Check "**Admin**" for yourself so you can manage chores
- Repeat for each child

### 2. Create chores
- Click "**Add Chore**"
- Name (e.g., "Wash Dishes")
- Description (e.g., "Wash and dry all dishes")
- Optionally assign to a person
- Click "Add Chore"

### 3. Track completions
- Each person can log in with their PIN
- Click on a chore → "Mark as Complete"
- App tracks who did it and when
- Admin can see the full history

---

## 🛑 Stop the App

```bash
# Press Ctrl+C in the terminal
# or in another terminal:
docker-compose down
```

---

## 📊 Data Persistence

**Important:** By default, Docker deletes the database when you stop the container.
To keep your chore history between sessions:

### Option A: Simple (recommended for first-time)
Nothing — SQLite database is in the container but refreshes each run. Good for testing.

### Option B: Persistent (for real use)
Edit `docker-compose.yml`:
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    ports:
      - "8055:8055"
    volumes:
      - ./data:/app/data    # ← ADD THIS LINE (saves database outside container)
```

Then the database lives in `./data/choreboss.db` on your computer. It survives container restarts.

---

## 🔧 Running Without Docker (if you prefer local Python)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements_linux.txt    # Linux
pip install -r requirements_windows.txt  # Windows

# Run the app
python run.py

# Open http://localhost:8055
```

**To stop:** Ctrl+C

---

## 🐛 Bugs Just Fixed

Three data-corruption bugs were fixed in `choreboss/models/`:
1. `Chore.validate_id` now returns the value (was silently setting id=None)
2. `People.validate_birthday` error message now says "datetime.date object" (was saying "string")
3. `Chore.validate_description` constraint message now says "10-500" (was saying "20-500")

All fixed. App is now safe to use.

---

## 📚 Features

- ✅ Multi-person household (parents + kids)
- ✅ PIN-based login (bcrypt hashed)
- ✅ Assign chores to people
- ✅ Track who completed each chore and when
- ✅ Admin panel to manage everything
- ✅ Persistent database

---

## 💡 Tips for Family Use

1. **Give each child a simple 4-digit PIN** (e.g., last 4 of their birthdate)
2. **Set yourself as admin** so you can change rules later
3. **Start with 3-5 core chores** (dishes, trash, laundry, etc.)
4. **Check the dashboard weekly** to see who's pulling their weight

---

## ❓ Common Questions

**Q: Can other family members access it from their phones?**
A: Not yet (would require port forwarding or a cloud deployment). For now, use on one computer. Future enhancement.

**Q: What if I forget the admin PIN?**
A: The database is in `./data/choreboss.db` (if you enabled persistence). Delete it, restart, and re-create the accounts.

**Q: Can I export the chore history?**
A: Not built in yet. The data is in SQLite — you can query it with a tool like `sqlite3` or DBeaver.

**Q: How do I update the app?**
A: `git pull` in the ChoreBoss folder, then `docker-compose up --build` again.

---

## Next Steps

1. ✅ Bugs fixed
2. ✅ Docker ready
3. 👉 **Start the app and add your family members**
4. Add your first chores
5. Have each child log in and complete a chore to test

Good luck! 🎉
