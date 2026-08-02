import asyncpg

from app.config import settings

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.database_url, min_size=2, max_size=10
        )
    return _pool


async def init_db():
    """Create all tables if they don't exist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                source_type TEXT NOT NULL CHECK (source_type IN ('scanner', 'paper', 'report')),
                url TEXT,
                category_count INT DEFAULT 0,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'done', 'review')),
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                source_id INT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                original_name TEXT NOT NULL,
                description TEXT,
                is_threat BOOL DEFAULT TRUE,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'mapped', 'needs_discussion')),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_categories_source_id ON categories(source_id);

            CREATE TABLE IF NOT EXISTS mappings (
                id SERIAL PRIMARY KEY,
                category_id INT UNIQUE NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                source_dim TEXT[],
                mech_dim TEXT[],
                target_dim TEXT[],
                vuln_tags TEXT[] DEFAULT '{}',
                confidence TEXT CHECK (confidence IN ('high', 'medium', 'low')),
                evidence TEXT,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_mappings_category_id ON mappings(category_id);

            CREATE TABLE IF NOT EXISTS dimension_values (
                id SERIAL PRIMARY KEY,
                dimension TEXT NOT NULL CHECK (dimension IN ('source', 'mech', 'target', 'vuln')),
                value_name TEXT NOT NULL,
                definition TEXT,
                examples TEXT,
                counter_examples TEXT,
                decision_rules TEXT,
                literature_ref TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(dimension, value_name)
            );
        """)

        # Migration: single-value TEXT dims -> TEXT[] (idempotent; no-op on fresh DBs)
        await conn.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'mappings' AND column_name = 'source_dim'
                      AND data_type = 'text'
                ) THEN
                    ALTER TABLE mappings
                        ALTER COLUMN source_dim TYPE TEXT[]
                        USING CASE WHEN source_dim IS NULL THEN NULL ELSE ARRAY[source_dim] END,
                        ALTER COLUMN mech_dim TYPE TEXT[]
                        USING CASE WHEN mech_dim IS NULL THEN NULL ELSE ARRAY[mech_dim] END,
                        ALTER COLUMN target_dim TYPE TEXT[]
                        USING CASE WHEN target_dim IS NULL THEN NULL ELSE ARRAY[target_dim] END;
                END IF;
            END $$;
        """)
