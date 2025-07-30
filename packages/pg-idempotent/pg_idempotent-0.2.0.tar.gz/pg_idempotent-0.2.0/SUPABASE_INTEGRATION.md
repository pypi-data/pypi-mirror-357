# Supabase Integration Guide

pg-idempotent now includes native Supabase integration to make your migration workflow safer and more robust.

## What It Does

The Supabase integration transforms your migration files to be **idempotent** - meaning they can be safely run multiple times without errors. This prevents issues when:

- Migration deployments fail halfway through
- Multiple developers run the same migrations
- CI/CD pipelines retry failed deployments
- You need to re-apply migrations during development

## Quick Start

### 1. Check Your Migration Files

From your Supabase project directory:

```bash
pg-idempotent supabase check
```

This scans all migration files in `supabase/migrations/` and reports which statements need to be made idempotent.

### 2. Preview Transformations

See what a specific migration would look like after transformation:

```bash
pg-idempotent supabase preview supabase/migrations/20240101000001_create_users.sql
```

### 3. Fix Migration Files

Transform all migration files to be idempotent:

```bash
# Dry run - see what would change without modifying files
pg-idempotent supabase fix --dry-run

# Apply transformations (creates backups automatically)
pg-idempotent supabase fix

# Output to a different directory
pg-idempotent supabase fix --output ./fixed-migrations
```

## Commands Reference

### `pg-idempotent supabase check [PATH]`

Analyze Supabase migration files for idempotency issues.

**Options:**
- `--schemas` - Also check declarative schema files in `supabase/schemas/`

**Examples:**
```bash
# Auto-detect Supabase project in current directory
pg-idempotent supabase check

# Check specific project
pg-idempotent supabase check /path/to/supabase/project

# Include schema files
pg-idempotent supabase check --schemas
```

### `pg-idempotent supabase fix [PATH]`

Transform migration files to be idempotent.

**Options:**
- `--output DIR` - Output transformed files to specified directory
- `--no-backup` - Don't create backup files
- `--schemas` - Also process declarative schema files
- `--dry-run` - Show changes without applying them

**Examples:**
```bash
# Transform files in place (with backups)
pg-idempotent supabase fix

# Output to different directory
pg-idempotent supabase fix --output ./safe-migrations

# Preview changes only
pg-idempotent supabase fix --dry-run
```

### `pg-idempotent supabase preview FILE`

Preview the transformation of a specific migration file.

**Options:**
- `--lines N` - Number of lines to show (default: 50)

**Examples:**
```bash
pg-idempotent supabase preview supabase/migrations/20240101000001_init.sql
pg-idempotent supabase preview migration.sql --lines 100
```

## How It Works

pg-idempotent wraps your SQL statements in PostgreSQL DO blocks with existence checks:

### Before (Original)
```sql
CREATE TYPE user_status AS ENUM ('active', 'inactive');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    status user_status DEFAULT 'active'
);

CREATE INDEX idx_users_email ON users(email);
```

### After (Idempotent)
```sql
DO $IDEMPOTENT$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type 
            WHERE typname = 'user_status'
            AND typnamespace = 'public'::regnamespace) THEN
        CREATE TYPE user_status AS ENUM ('active', 'inactive');
    END IF;
END $IDEMPOTENT$;

DO $IDEMPOTENT_001$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users') THEN
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            status user_status DEFAULT 'active'
        );
    END IF;
END $IDEMPOTENT_001$;

DO $IDEMPOTENT_002$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname = 'idx_users_email') THEN
        CREATE INDEX idx_users_email ON users(email);
    END IF;
END $IDEMPOTENT_002$;
```

## Supported SQL Statements

- `CREATE TABLE` → Checks `information_schema.tables`
- `CREATE TYPE` → Checks `pg_type`
- `CREATE INDEX` → Checks `pg_indexes`
- `CREATE FUNCTION` → Checks `pg_proc` (or uses `CREATE OR REPLACE`)
- `CREATE POLICY` → Checks `pg_policies`
- `CREATE TRIGGER` → Checks `pg_trigger`
- `CREATE VIEW` → Checks `information_schema.views`
- `ALTER TABLE` → Uses exception handling for duplicates
- `GRANT` → Checks `information_schema.table_privileges`

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Deploy to Supabase
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup pg-idempotent
        run: pip install pg-idempotent
      
      - name: Make migrations idempotent
        run: |
          pg-idempotent supabase fix --output ./safe-migrations
          
      - name: Deploy to Supabase
        run: |
          # Copy safe migrations back
          cp -r ./safe-migrations/* ./supabase/migrations/
          supabase db push
```

### Local Development Workflow

1. **Create migrations normally:**
   ```bash
   supabase migration new create_users_table
   # Edit the generated migration file
   ```

2. **Make them idempotent before applying:**
   ```bash
   pg-idempotent supabase fix
   ```

3. **Apply migrations:**
   ```bash
   supabase db reset  # or supabase db push
   ```

## Benefits

- **Safe Re-runs**: Migration failures won't leave your database in an inconsistent state
- **Team Collaboration**: Multiple developers can safely run the same migrations
- **CI/CD Robustness**: Deployment pipelines become more resilient to partial failures
- **Development Workflow**: Safely re-run migrations during development without dropping the database

## Advanced Usage

### Processing Both Migrations and Schemas

```bash
pg-idempotent supabase check --schemas
pg-idempotent supabase fix --schemas
```

### Batch Processing with Supabase Detection

```bash
# The batch command can auto-detect Supabase projects
pg-idempotent batch . --supabase --output-dir ./fixed
```

### Custom File Patterns

```bash
# Process only specific migration files
pg-idempotent batch supabase/migrations/ --pattern "*_create_*.sql"
```

## Troubleshooting

### "No Supabase project found"
- Ensure you're running from a directory containing a `supabase/` folder
- Check that `supabase/config.toml` exists

### "Validation issues found"
- Some complex dollar-quoted strings may trigger validation warnings
- These are usually safe to ignore for PostgreSQL functions

### Backup Files
- Backups are stored in `.pg-idempotent-backups/` by default
- Use `--no-backup` to disable automatic backups

## Examples

Check out the `examples/` directory for sample migration files and their transformed versions.