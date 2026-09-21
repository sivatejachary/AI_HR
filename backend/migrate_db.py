import sqlite3

def migrate():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()

    # Migrate jobs table
    job_cols = [c[1] for c in cursor.execute('PRAGMA table_info(jobs)').fetchall()]
    for col in ['google_form_id', 'google_form_url', 'google_responder_url']:
        if col not in job_cols:
            cursor.execute(f'ALTER TABLE jobs ADD COLUMN {col} TEXT')
            print(f"Added column '{col}' to table 'jobs'")

    # Migrate forms table
    form_cols = [c[1] for c in cursor.execute('PRAGMA table_info(forms)').fetchall()]
    for col in ['google_form_id', 'google_form_url', 'google_responder_url']:
        if col not in form_cols:
            cursor.execute(f'ALTER TABLE forms ADD COLUMN {col} TEXT')
            print(f"Added column '{col}' to table 'forms'")

    # Migrate integrations table
    integ_cols = [c[1] for c in cursor.execute('PRAGMA table_info(integrations)').fetchall()]
    for col in ['user_id', 'google_account_email', 'google_subject_id', 'access_token_encrypted', 'refresh_token_encrypted', 'token_expires_at', 'scopes', 'status', 'config_json']:
        if col not in integ_cols:
            cursor.execute(f'ALTER TABLE integrations ADD COLUMN {col} TEXT')
            print(f"Added column '{col}' to table 'integrations'")

    conn.commit()
    conn.close()
    print("Database Schema Migration Completed Successfully!")

if __name__ == '__main__':
    migrate()
