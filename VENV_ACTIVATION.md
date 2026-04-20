# 🔧 Quick Fix for Virtual Environment Activation

## The Problem
When you run `python api_run.py` without activating the venv, Python can't find the installed packages.

## The Solution (Pick One)

### ✅ Method 1: Use the Startup Script (EASIEST)

```bash
cd /srv/github/ChoreBoss
bash start_backend.sh
```

This script automatically:
- Checks if venv exists
- Activates it
- Sets environment variables
- Starts FastAPI

### ✅ Method 2: Manual Activation (What You Should Do)

```bash
cd /srv/github/ChoreBoss
source .venv/bin/activate
python api_run.py
```

The `source .venv/bin/activate` command:
- Activates the virtual environment
- Changes your `PATH` so Python finds packages
- Modifies your prompt to show `(.venv)`

### ✅ Method 3: Use Full Path to Python

```bash
cd /srv/github/ChoreBoss
.venv/bin/python api_run.py
```

This runs the Python from the venv directly without needing to activate.

### ✅ Method 4: One-Liner

```bash
cd /srv/github/ChoreBoss && source .venv/bin/activate && python api_run.py
```

---

## Verify Venv is Active

Look for `(.venv)` at the start of your prompt:

```
(.venv) leto@nuc:~/ChoreBoss$  ← Good! Venv is active
leto@nuc:~/ChoreBoss$          ← Bad! Venv is NOT active
```

Or check which Python:

```bash
which python
# Should print: /srv/github/ChoreBoss/.venv/bin/python

python --version
# Should work without errors
```

---

## Complete Walkthrough

### Terminal Session Example

```bash
# 1. Navigate to project
leto@nuc:~$ cd /srv/github/ChoreBoss
leto@nuc:ChoreBoss$

# 2. Activate venv (notice the (.venv) prefix)
leto@nuc:ChoreBoss$ source .venv/bin/activate
(.venv) leto@nuc:ChoreBoss$

# 3. Optional: Set database environment
(.venv) leto@nuc:ChoreBoss$ export DATABASE_URL="sqlite+aiosqlite:///choreboss.db"

# 4. Start FastAPI
(.venv) leto@nuc:ChoreBoss$ python api_run.py
🚀 ChoreBoss API starting...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Done! Server is running.

---

## In Another Terminal (For Frontend)

```bash
# Terminal 2
leto@nuc:~$ cd /srv/github/ChoreBoss
leto@nuc:ChoreBoss$ source .venv/bin/activate
(.venv) leto@nuc:ChoreBoss$ python flask_bridge.py
🌐 Flask Frontend starting...
 * Running on http://0.0.0.0:8055
```

---

## Deactivate When Done

```bash
# To exit the virtual environment
(.venv) leto@nuc:ChoreBoss$ deactivate
leto@nuc:ChoreBoss$  # Back to normal
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"

**Problem:** Venv is not activated  
**Solution:**
```bash
source .venv/bin/activate
python api_run.py
```

### "venv: command not found"

**Problem:** Python venv module not installed  
**Solution:**
```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### "which python" points to /usr/bin/python

**Problem:** Venv is not activated, using system Python  
**Solution:**
```bash
source .venv/bin/activate
which python  # Should now show .venv/bin/python
```

---

## Pro Tips

### Make it Automatic (Add to ~/.bashrc or ~/.zshrc)

```bash
# Add this to your shell config
alias choreboss="cd /srv/github/ChoreBoss && source .venv/bin/activate"
```

Then just type:
```bash
choreboss
python api_run.py
```

### Check Installed Packages

```bash
# Only works when venv is active
source .venv/bin/activate
pip list
```

### Reinstall Dependencies If Needed

```bash
source .venv/bin/activate
pip install -e ".[dev]"  # Installs everything
```

---

## Summary

**The key is: `source .venv/bin/activate`**

Do this first, then any `python` command will use the venv's packages.

Or use the startup script:
```bash
bash start_backend.sh
```

**Everything is set up and ready!** 🚀
