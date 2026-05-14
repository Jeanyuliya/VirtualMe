-- Migration 20260514: add source_question_ids column to anchors table
--
-- Context: PR #4 (issue #3 fix) added source_question_ids to anchors via
-- CREATE TABLE IF NOT EXISTS in schema.sql, which skips existing tables.
-- This migration adds the column to pre-PR-#4 databases via ALTER TABLE.
--
-- The application executes this idempotently via
-- _apply_schema_migrations() in src/virtualme/storage/db.py, which
-- checks PRAGMA table_info(anchors) before running ALTER TABLE.
--
-- This .sql file exists for human readability and audit only. It is
-- NOT automatically executed by init_db.py.

ALTER TABLE anchors
ADD COLUMN source_question_ids TEXT NOT NULL DEFAULT '[]';
