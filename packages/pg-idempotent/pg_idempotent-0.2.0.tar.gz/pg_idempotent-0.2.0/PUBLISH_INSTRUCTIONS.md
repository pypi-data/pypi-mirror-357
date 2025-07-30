# Publishing pg-idempotent to PyPI

The package is ready to publish! Here's exactly what you need to do:

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org/account/register/
2. **API Token**: Generate at https://pypi.org/manage/account/token/ (scope: "Entire account")

## Publishing Steps

### Option 1: Using Environment Variable (Recommended)

```bash
# Set your PyPI token
export UV_PUBLISH_TOKEN="pypi-your-token-here"

# Build the package (already done)
uv build

# Publish to PyPI
uv publish
```

### Option 2: Interactive Authentication

```bash
# UV will prompt for credentials
uv publish --username __token__ --password pypi-your-token-here
```

## What Gets Published

- **Package**: `pg-idempotent` version `0.2.0`
- **Core features**: Basic SQL transformation to idempotent versions
- **Supabase integration**: Native Supabase migration file processing
- **CLI commands**: 
  - `pg-idempotent transform`
  - `pg-idempotent supabase check/fix/preview`
  - `pg-idempotent batch`

## Installation Options for Users

```bash
# Basic installation (recommended for most users)
pip install pg-idempotent

# With all optional features
pip install pg-idempotent[all]

# Advanced features only
pip install pg-idempotent[advanced]
```

## Verify Publication

After publishing, test the installation:

```bash
# Install from PyPI in a fresh environment
pip install pg-idempotent

# Test basic functionality
pg-idempotent --help
pg-idempotent supabase --help
```

## Files Ready for Publication

- ✅ `dist/pg_idempotent-0.2.0-py3-none-any.whl` 
- ✅ `dist/pg_idempotent-0.2.0.tar.gz`
- ✅ Package metadata configured
- ✅ Dependencies optimized (core dependencies + optional extras)
- ✅ All tests passing (13/13 integration tests ✓)

## Features Included in v0.2.0

### Core Features
- Transform PostgreSQL SQL statements to idempotent versions
- Wrap statements in DO blocks with existence checks
- Support for tables, indexes, types, functions, policies, etc.
- Beautiful CLI with Rich terminal output

### Supabase Integration ⭐
- **Auto-detection** of Supabase projects
- **Batch processing** of migration files in `supabase/migrations/`
- **Schema support** for declarative files in `supabase/schemas/`
- **Safety features** with automatic backups
- **Preview mode** to see transformations before applying

### CLI Commands
```bash
# Basic transformation
pg-idempotent transform file.sql
pg-idempotent batch migrations/ --recursive

# Supabase workflow
pg-idempotent supabase check        # Analyze migration files
pg-idempotent supabase fix         # Transform to idempotent
pg-idempotent supabase preview file.sql  # Preview transformation

# Advanced options
pg-idempotent supabase fix --dry-run --output ./safe-migrations
```

## Post-Publication

1. **Test installation** from PyPI
2. **Update documentation** with installation instructions
3. **Share with community** - this solves a real PostgreSQL migration problem!

The package is production-ready and will immediately help developers with safer PostgreSQL migrations and Supabase workflows.