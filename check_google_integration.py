import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_hr_db")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    print("Checking integrations table...")
    res = db.execute(text("SELECT id, platform_name, is_connected, access_token_encrypted FROM integrations;")).fetchall()
    print("Integrations:")
    for r in res:
        print(" ", r)
        
    print("\nChecking Google Integrations table...")
    g_res = db.execute(text("SELECT * FROM google_integrations;")).fetchall()
    print("Google Integrations:")
    for gr in g_res:
        print(" ", gr)
        
    print("\nChecking Jobs table...")
    jobs = db.execute(text("SELECT id, title, google_form_id, google_form_url FROM jobs LIMIT 5;")).fetchall()
    print("Jobs:")
    for j in jobs:
        print(" ", j)
finally:
    db.close()
