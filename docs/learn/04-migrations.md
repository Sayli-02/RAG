# Database Migrations and Alembic

1. **One-line definition**
Database migrations are structured, version-controlled scripts that systematically apply and revert changes to a database schema over time.

2. **Why it exists** (the problem it solves)
As software systems evolve, tables need new columns, indexes, and constraints. Updating database schemas manually via interactive SQL shells causes drift between environments (development, testing, production), cannot be tracked in Git, and makes rollbacks risky. Migrations ensure that any database instance can be brought to any desired schema version deterministically and safely.

3. **Analogy**
Migrations are like architectural blueprints and building permits for a skyscraper. When remodeling a floor, you don't knock down random walls on the spot; you record a dated change order specifying exactly what to build (upgrade) and how to restore it if plans change (downgrade). Any builder can follow the blueprints to reproduce the exact same building state.

4. **How it works** (step by step)
- **Step 1: Migration script creation**: Alembic creates a timestamped script with a unique revision ID containing two functions: `upgrade()` (to apply changes) and `downgrade()` (to revert them).
- **Step 2: Tracking table**: The database maintains a special table named `alembic_version` storing the single current revision ID.
- **Step 3: Execution**: When running `alembic upgrade head`, Alembic reads `alembic_version`, finds the unapplied migration scripts in chronological order, executes their `upgrade()` functions inside a transaction, and updates `alembic_version`.

5. **Where it is in FinScope** (file + function)
- Configuration: [backend/alembic/env.py](file:///c:/Users/Sayli/Downloads/RAG/backend/alembic/env.py#L1-L67)
- Baseline migration: [backend/alembic/versions/0001_initial_schema.py](file:///c:/Users/Sayli/Downloads/RAG/backend/alembic/versions/0001_initial_schema.py#L18-L230) (`upgrade()` & `downgrade()`)

6. **Common mistakes**
- Manually altering database tables in production without writing and recording an Alembic migration.
- Modifying a migration script after it has already been applied and committed to a shared repository, leading to divergent migration histories across team members.
- Writing non-reversible migrations with empty `downgrade()` functions.

7. **Check yourself**
1. *What table does Alembic use in PostgreSQL to remember which migration is currently applied?*
2. *What is the difference between running migrations 'online' versus 'offline' (`--sql`)?*
3. *Why must the vector extension (`CREATE EXTENSION IF NOT EXISTS vector;`) be executed in the very first migration?*

---
**Answers:**
1. The `alembic_version` table.
2. 'Online' mode connects directly to a live database engine and executes DDL statements immediately; 'offline' mode generates raw SQL statements to stdout/file without needing a live connection.
3. Because tables created in that migration (like `document_chunks`) depend on the custom `Vector` data type provided by the extension; without it, table creation fails.

