-- Migration 20260514: add current_question_id column to sessions table
--
-- Context: v0.5 current-question tracking stores the question that the
-- next user answer is expected to answer at session scope.
--
-- The application executes this idempotently via
-- _apply_schema_migrations() in src/virtualme/storage/db.py, which
-- checks PRAGMA table_info(sessions) before running ALTER TABLE.
--
-- This .sql file exists for human readability and audit only. It is
-- NOT automatically executed by init_db.py.

ALTER TABLE sessions
ADD COLUMN current_question_id TEXT;

