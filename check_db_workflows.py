import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_hr_db")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    print("Checking database tables...")
    res = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")).fetchall()
    print("Tables:", [r[0] for r in res])
    
    # Check Candidate Shiva
    cand = db.execute(text("SELECT id, name, email FROM candidates WHERE name='Shiva';")).fetchone()
    print("Candidate Shiva:", cand)
    
    # Check Candidate Workflows
    cwfs = db.execute(text("SELECT id, candidate_id, workflow_id, current_step_id, status FROM candidate_workflows;")).fetchall()
    print("Candidate Workflows count:", len(cwfs))
    for cw in cwfs:
        print(" ", cw)
        
    # Check Candidate Workflow Steps
    cw_steps = db.execute(text("SELECT id, candidate_workflow_id, step_name, schedule_type, scheduled_at, status FROM candidate_workflow_steps;")).fetchall()
    print("Candidate Workflow Steps count:", len(cw_steps))
    for cs in cw_steps:
        print(" ", cs)
finally:
    db.close()
