import sys
import logging
from datetime import datetime
from sqlalchemy import text, inspect
from app.db.database import engine, Base
from app.models.domain import (
    Organization, User, Job, Candidate, Application, HiringWorkflow, WorkflowStep,
    Integration, Role, Permission, UserRoleAssoc, RolePermission, UserSession
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_postgres")

def auto_migrate_postgres_columns():
    """
    Scans SQLAlchemy Base metadata and issues PostgreSQL 'ALTER TABLE ... ADD COLUMN IF NOT EXISTS'
    for every column defined in domain models to upgrade pre-existing tables dynamically.
    """
    logger.info("2a. Running PostgreSQL auto-column migration ('ADD COLUMN IF NOT EXISTS')...")
    with engine.connect() as conn:
        for table_name, table in Base.metadata.tables.items():
            for column in table.columns:
                col_name = column.name
                # Determine PostgreSQL type representation
                col_type = column.type.compile(engine.dialect)

                # Format default clause if simple literal
                default_clause = ""
                if column.default is not None and column.default.arg is not None:
                    if isinstance(column.default.arg, (bool, int, float, str)):
                        default_str = str(column.default.arg).lower() if isinstance(column.default.arg, bool) else f"'{column.default.arg}'" if isinstance(column.default.arg, str) else str(column.default.arg)
                        default_clause = f" DEFAULT {default_str}"

                alter_stmt = f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS "{col_name}" {col_type}{default_clause};'
                try:
                    conn.execute(text(alter_stmt))
                except Exception as e:
                    logger.warning(f"   Column migration notice for {table_name}.{col_name}: {e}")
        conn.commit()
    logger.info("   PostgreSQL column auto-migration completed.")

def init_postgres_db():
    logger.info("============================================================")
    logger.info("   RECRUITMENT PRO — POSTGRESQL DB INITIALIZER")
    logger.info("============================================================")
    
    with engine.connect() as conn:
        logger.info("1. Ensuring PostgreSQL UUID extension 'uuid-ossp'...")
        try:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.commit()
            logger.info("   Extension 'uuid-ossp' is ready.")
        except Exception as e:
            logger.warning(f"   Note on UUID extension: {e}")

    logger.info("2. Creating all domain table schemas via SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    logger.info("   Base metadata create_all completed.")

    # Upgrade pre-existing tables to include any missing columns
    auto_migrate_postgres_columns()

    # Seed baseline records if missing
    from sqlalchemy.orm import Session
    with Session(engine) as db:
        logger.info("3. Seeding default Organization 'org-default'...")
        org = db.query(Organization).filter(Organization.id == "org-default").first()
        if not org:
            org = Organization(
                id="org-default",
                name="Recruitment Pro Enterprise",
                slug="recruitment-pro-default",
                legal_name="Recruitment Pro Corp",
                industry="Software & AI",
                timezone="UTC",
                status="ACTIVE"
            )
            db.add(org)
            db.commit()
            logger.info("   Created default Organization 'org-default'.")
        else:
            logger.info("   Default Organization 'org-default' exists.")

        logger.info("4. Seeding default User 'user-hr-admin'...")
        user = db.query(User).filter(User.id == "user-hr-admin").first()
        if not user:
            user = User(
                id="user-hr-admin",
                organization_id="org-default",
                first_name="HR",
                last_name="Admin",
                name="HR Administrator",
                email="hr.admin@workspace.internal",
                hashed_password="scrypt:32768:8:1$default_hash",
                role="HR_ADMIN",
                status="ACTIVE"
            )
            db.add(user)
            db.commit()
            logger.info("   Created default User 'user-hr-admin'.")
        else:
            logger.info("   Default User 'user-hr-admin' exists.")

        logger.info("5. Seeding default System Roles...")
        roles = [
            ("SUPER_ADMIN", "Super Administrator with full global privileges"),
            ("ORG_ADMIN", "Organization Administrator"),
            ("HR_ADMIN", "HR Administrator managing recruitment pipelines"),
            ("RECRUITER", "Recruiter conducting sourcing and candidate reviews"),
            ("HIRING_MANAGER", "Hiring Manager approving candidates and offers"),
            ("INTERVIEWER", "Interviewer carrying out candidate evaluations"),
            ("VIEWER", "Read-only viewer")
        ]
        for r_name, r_desc in roles:
            r = db.query(Role).filter(Role.organization_id == "org-default", Role.name == r_name).first()
            if not r:
                db.add(Role(
                    organization_id="org-default",
                    name=r_name,
                    description=r_desc,
                    is_system_role=True
                ))
        db.commit()
        logger.info("   System Roles verified.")

        logger.info("6. Seeding default HiringWorkflow 'wf-se-1'...")
        wf = db.query(HiringWorkflow).filter(HiringWorkflow.id == "wf-se-1").first()
        if not wf:
            wf = HiringWorkflow(
                id="wf-se-1",
                organization_id="org-default",
                name="Software Engineer Hiring Workflow",
                description="Default standard hiring workflow for software engineering candidates",
                is_active=True,
                created_by="user-hr-admin"
            )
            db.add(wf)
            db.commit()
            logger.info("   Created default HiringWorkflow 'wf-se-1'.")
        else:
            logger.info("   Default HiringWorkflow 'wf-se-1' exists.")

    logger.info("============================================================")
    logger.info("   POSTGRESQL INITIALIZATION & SEEDING PASSED PERFECTLY!")
    logger.info("============================================================")

if __name__ == "__main__":
    init_postgres_db()
