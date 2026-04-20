# Migration Checklist

Use this before every migration to ensure quality and reversibility.

---

## Pre-Migration (Planning)

- [ ] What is the business reason for this change?
- [ ] Will this be backward compatible?
- [ ] Does this require a data migration?
- [ ] Is there a rollback plan?
- [ ] Who needs to approve this?

---

## Pre-Generation (Model Change)

- [ ] Update model in `choreboss/models/`
- [ ] Add type hints
- [ ] Add docstring for new field
- [ ] Run existing tests (should still pass)
- [ ] Check field constraints (nullable, default, etc.)

---

## Generation (Create Migration)

```bash
# Generate migration
alembic revision --autogenerate -m "Describe the change"

# Review the generated file
cat migrations/versions/<revision_id>_describe_the_change.py
```

---

## Review (Quality Check)

- [ ] Migration file created
- [ ] Revision ID is unique
- [ ] Upgrade function implements the change
- [ ] Downgrade function properly reverts
- [ ] No manual SQL unless necessary
- [ ] Column names match model
- [ ] Constraints match model
- [ ] Indexes are appropriate
- [ ] Foreign keys reference correct tables
- [ ] No hardcoded data (use op.execute for data)

---

## Testing (Local)

### Test 1: Apply Migration
```bash
alembic upgrade head
# Verify tables/columns exist
sqlite3 choreboss.db ".schema"
```

### Test 2: Revert Migration
```bash
alembic downgrade -1
# Verify tables/columns removed
sqlite3 choreboss.db ".schema"
```

### Test 3: Re-apply Migration
```bash
alembic upgrade head
# Verify tables/columns exist again
sqlite3 choreboss.db ".schema"
```

**Checklist:**
- [ ] Upgrade succeeds
- [ ] Downgrade succeeds
- [ ] Re-upgrade succeeds
- [ ] No SQL errors
- [ ] Schema correct after upgrade
- [ ] Schema restored after downgrade

---

## Testing (Data Integrity)

If migration affects data:

- [ ] Test with sample data
- [ ] Verify no data loss on upgrade
- [ ] Verify data restored on downgrade (if applicable)
- [ ] Check referential integrity
- [ ] Validate constraints
- [ ] Test edge cases (NULL values, etc.)

---

## Code Review (If Required)

Prepare for code review:

- [ ] Explain the change in commit message
- [ ] Explain why this migration is needed
- [ ] Confirm no data loss
- [ ] Show upgrade/downgrade worked
- [ ] List any assumptions

**Example commit message:**
```
db: add priority field to chores table

- New field: chores.priority (Integer, default=1)
- Allows ranking chores by importance
- Backward compatible: old records get default priority=1
- Migration tested: upgrade ✓ downgrade ✓ upgrade ✓
- No data loss on upgrade/downgrade
```

---

## Commit (Git)

```bash
# Add migration file
git add migrations/versions/<revision_id>_describe_the_change.py

# Add any related code changes
git add choreboss/models/chore.py

# Commit with message
git commit -m "db: add priority field to chores table"

# Verify commit
git log -1 --stat
```

---

## Pre-Deployment (Production)

**Before deploying to production:**

- [ ] Migration tested locally (upgrade/downgrade)
- [ ] Committed to main branch
- [ ] Code reviewed and approved
- [ ] Tested in staging environment (if available)
- [ ] Backup of production database taken
- [ ] Rollback plan documented
- [ ] Team notified of upcoming change
- [ ] Deployment window scheduled

---

## Deployment

```bash
# Pull latest code
git pull origin main

# Run migration
alembic upgrade head

# Verify application still works
# (run smoke tests, check logs, etc.)

# Notify team of success
```

---

## Post-Deployment

- [ ] Verify database schema matches expectations
- [ ] Run smoke tests
- [ ] Monitor application logs
- [ ] Check for errors in logs
- [ ] Verify functionality works
- [ ] Backup database (success state)
- [ ] Document deployment in runbook
- [ ] Update team

---

## Emergency Rollback

If something goes wrong:

```bash
# Revert to previous migration
alembic downgrade -1

# Verify schema reverted
alembic current

# Check database
sqlite3 choreboss.db ".schema"

# Notify team and investigate
```

---

## Common Mistakes to Avoid

❌ **Don't:**
- Edit migration file after committing
- Forget downgrade() function
- Create migration without testing downgrade
- Hardcode usernames/passwords in migration
- Delete data without backup
- Use migration for application logic
- Forget to commit migration file
- Deploy without testing in staging

✅ **Do:**
- Test both upgrade and downgrade locally
- Write clear, descriptive messages
- Include both upgrade() and downgrade()
- Use descriptive column/table names
- Add constraints and indexes
- Review migration before committing
- Test in staging before production
- Keep migrations focused (one logical change)

---

## Migration Templates

### Add New Table
```python
def upgrade() -> None:
    op.create_table(
        'new_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('new_table')
```

### Add Column to Existing Table
```python
def upgrade() -> None:
    op.add_column('chores', 
        sa.Column('priority', sa.Integer(), default=1))

def downgrade() -> None:
    op.drop_column('chores', 'priority')
```

### Add Constraint
```python
def upgrade() -> None:
    op.create_unique_constraint('uq_chores_name', 'chores', ['name'])

def downgrade() -> None:
    op.drop_constraint('uq_chores_name', 'chores')
```

### Data Migration
```python
def upgrade() -> None:
    # Add column first
    op.add_column('chores', 
        sa.Column('category', sa.String(50), nullable=True))
    
    # Migrate data
    op.execute("UPDATE chores SET category = 'general' WHERE category IS NULL")
    
    # Make not nullable
    op.alter_column('chores', 'category', nullable=False)

def downgrade() -> None:
    op.drop_column('chores', 'category')
```

---

## Useful Commands

```bash
# View pending migrations (not applied)
alembic upgrade head --sql

# View migration history
alembic history -v

# Show current state
alembic current

# Generate migration with preview
alembic revision --autogenerate -m "Test" --sql

# View heads (latest revisions)
alembic heads

# View branches
alembic branches

# Check for issues
alembic check
```

---

## Status Checklist Summary

**For Every Migration:**
- [ ] Plan documented
- [ ] Model updated
- [ ] Migration generated
- [ ] Migration reviewed
- [ ] Tested: upgrade ✓
- [ ] Tested: downgrade ✓
- [ ] Tested: upgrade again ✓
- [ ] Committed to git
- [ ] Ready for deployment

**Pre-Deployment:**
- [ ] Staging tested
- [ ] Backup taken
- [ ] Team notified
- [ ] Rollback plan ready

**Post-Deployment:**
- [ ] Schema verified
- [ ] Tests passed
- [ ] Logs checked
- [ ] Team updated
