# Puper API Database Migrations Guide

## Overview

This project uses Alembic for database schema migrations. Alembic is a lightweight database migration tool for use with SQLAlchemy.

## Files Structure

```
puper/
├── alembic.ini                    # Alembic configuration
├── migrate.py                     # Migration helper script
├── alembic/
│   ├── env.py                     # Alembic environment
│   ├── script.py.mako             # Migration template
│   └── versions/                  # Migration files
│       └── 001_initial_schema.py  # Initial schema
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Database
Make sure PostgreSQL with PostGIS is running and your `.env` file is configured:
```env
DATABASE_URL=postgresql://puper_user:puper_password@localhost:5432/puper
```

### 3. Run Initial Migration
```bash
# Using the helper script
python migrate.py upgrade

# Or using Alembic directly
alembic upgrade head
```

## Migration Helper Script

The `migrate.py` script provides easy commands for common migration tasks:

### Available Commands

```bash
# Initialize Alembic (first time setup)
python migrate.py init

# Create a new migration
python migrate.py create "Add new column to users table"

# Upgrade database to latest
python migrate.py upgrade

# Upgrade to specific revision
python migrate.py upgrade abc123

# Downgrade to previous revision
python migrate.py downgrade -1

# Downgrade to specific revision
python migrate.py downgrade abc123

# Show migration history
python migrate.py history

# Show current database revision
python migrate.py current

# Show head revisions
python migrate.py heads

# Stamp database with revision (without running migrations)
python migrate.py stamp head

# Show help
python migrate.py help
```

## Using Alembic Directly

If you prefer to use Alembic commands directly:

### Basic Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123

# Show current revision
alembic current

# Show migration history
alembic history --verbose

# Show head revisions
alembic heads
```

## Migration Workflow

### 1. Making Model Changes

1. Edit your SQLAlchemy models in `main.py`
2. Create a new migration:
   ```bash
   python migrate.py create "Description of your changes"
   ```
3. Review the generated migration file in `alembic/versions/`
4. Apply the migration:
   ```bash
   python migrate.py upgrade
   ```

### 2. Example: Adding a New Column

1. Add the column to your model:
   ```python
   class User(Base):
       # ... existing columns ...
       new_column = Column(String(100), nullable=True)
   ```

2. Generate migration:
   ```bash
   python migrate.py create "Add new_column to users table"
   ```

3. Review the generated file and apply:
   ```bash
   python migrate.py upgrade
   ```

### 3. Example: Creating a New Table

1. Define the new model in `main.py`
2. Generate migration:
   ```bash
   python migrate.py create "Add new_table"
   ```
3. Apply migration:
   ```bash
   python migrate.py upgrade
   ```

## Production Deployment

### 1. Backup Database
Always backup your production database before running migrations:
```bash
pg_dump -h hostname -U username -d database_name > backup.sql
```

### 2. Run Migrations
```bash
# Set production environment
export DATABASE_URL="postgresql://user:pass@prod-host:5432/puper"

# Run migrations
python migrate.py upgrade
```

### 3. Verify Migration
```bash
# Check current revision
python migrate.py current

# Verify database schema
psql $DATABASE_URL -c "\dt"  # List tables
```

## Troubleshooting

### Common Issues

1. **"Target database is not up to date"**
   ```bash
   # Check current revision
   python migrate.py current
   
   # Upgrade to latest
   python migrate.py upgrade
   ```

2. **"Can't locate revision identified by 'abc123'"**
   ```bash
   # Check available revisions
   python migrate.py history
   ```

3. **PostGIS Extension Error**
   ```bash
   # Connect to database and create extension manually
   psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   ```

4. **Permission Denied**
   - Ensure database user has CREATE privileges
   - For PostGIS, user needs SUPERUSER or specific extension privileges

### Manual Recovery

If migrations get out of sync:

1. **Check current state:**
   ```bash
   python migrate.py current
   python migrate.py heads
   ```

2. **Stamp database with correct revision:**
   ```bash
   python migrate.py stamp head
   ```

3. **Or reset to specific revision:**
   ```bash
   python migrate.py stamp abc123
   ```

## Best Practices

### 1. Migration Safety
- Always review generated migrations before applying
- Test migrations on a copy of production data
- Keep migrations small and focused
- Never edit applied migrations

### 2. Naming Conventions
- Use descriptive migration messages
- Include ticket/issue numbers if applicable
- Examples:
  - "Add email verification to users"
  - "Create restroom_photos table"
  - "Add indexes for search performance"

### 3. Data Migrations
For complex data transformations, create separate data migration scripts:
```python
def upgrade():
    # Schema changes
    op.add_column('users', sa.Column('full_name', sa.String(100)))
    
    # Data migration
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET full_name = first_name || ' ' || last_name"
    )
```

### 4. Rollback Strategy
- Always test downgrade migrations
- Consider data loss implications
- Document any manual steps required

## Environment-Specific Migrations

### Development
```bash
# Quick iteration
python migrate.py create "WIP: testing new feature"
python migrate.py upgrade
# ... test ...
python migrate.py downgrade -1  # rollback if needed
```

### Staging
```bash
# Mirror production process
python migrate.py upgrade
# ... run tests ...
```

### Production
```bash
# Careful, deliberate process
python migrate.py current  # check state
python migrate.py upgrade  # apply migrations
python migrate.py current  # verify
```

## Integration with Docker

When using Docker Compose, migrations can be run automatically:

```yaml
# In docker-compose.yml
services:
  api:
    # ... other config ...
    command: >
      sh -c "python migrate.py upgrade &&
             uvicorn main:app --host 0.0.0.0 --port 8000"
```

Or run manually in container:
```bash
docker-compose exec api python migrate.py upgrade
```
