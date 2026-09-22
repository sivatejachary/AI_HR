import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_hr_db")

if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+psycopg2://", 1)

print(f"Connecting to Render PostgreSQL DB...")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db = Session()

migrations = [
    # workflow_steps columns
    "ALTER TABLE workflow_steps ADD COLUMN IF NOT EXISTS schedule_type VARCHAR(32) DEFAULT 'IMMEDIATE';",
    "ALTER TABLE workflow_steps ADD COLUMN IF NOT EXISTS fixed_timestamp TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE workflow_steps ADD COLUMN IF NOT EXISTS relative_delay_minutes INTEGER DEFAULT 0;",
    "ALTER TABLE workflow_steps ADD COLUMN IF NOT EXISTS executor VARCHAR(64) DEFAULT 'AI_HR_AGENT';",
    "ALTER TABLE workflow_steps ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;",
    "ALTER TABLE workflow_steps ADD COLUMN IF NOT EXISTS allow_skip BOOLEAN DEFAULT TRUE;",

    # candidate_workflow_steps columns
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS schedule_type VARCHAR(32) DEFAULT 'IMMEDIATE';",
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS fixed_timestamp TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS relative_delay_minutes INTEGER DEFAULT 0;",
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS executor VARCHAR(64) DEFAULT 'AI_HR_AGENT';",
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE;",
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS allow_skip BOOLEAN DEFAULT TRUE;",
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE candidate_workflow_steps ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE;"
]

try:
    for m in migrations:
        print(f"Executing: {m}")
        db.execute(text(m))
    db.commit()
    print("\n[SUCCESS] PostgreSQL migrations applied successfully to Render database!")
except Exception as e:
    db.rollback()
    print(f"\n[ERROR] Migration failed: {e}")
finally:
    db.close()
