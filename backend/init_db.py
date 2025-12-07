#!/usr/bin/env python3
"""Initialize the Cloud SQL database for the Lumen project"""

import os
import sqlalchemy
from google.cloud.sql.connector import Connector
from dotenv import load_dotenv
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

def init_connection_pool(connector: Connector) -> sqlalchemy.engine.base.Engine:
    """Initializes a connection pool for a Cloud SQL instance."""

    def getconn() -> sqlalchemy.engine.base.Connection:
        # Connect to the default 'postgres' database to create 'lumen_db' if it doesn't exist
        temp_conn = connector.connect(
            os.environ["DB_CONNECTION_STRING"],
            "pg8000",
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            db="postgres", # Connect to default postgres database
        )
        temp_conn.autocommit = True # Ensure autocommit for CREATE DATABASE

        # Check if lumen_db exists, create if not
        cursor = temp_conn.cursor()
        db_name = os.environ["DB_NAME"]
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{os.environ["DB_NAME"]}"')
        cursor.close()
        temp_conn.close()

        # Now connect to the actual lumen_db
        conn = connector.connect(
            os.environ["DB_CONNECTION_STRING"],
            "pg8000",
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            db=os.environ["DB_NAME"],
        )
        return conn

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool

def migrate_db(pool: sqlalchemy.engine.base.Engine) -> None:
    """Creates all tables in the database."""
    with open("/home/cdc/Storage/NVMe/projects/wasenet/lumen-gcp/backend/database/schema.sql") as f:
        schema = f.read()

    with pool.connect() as db_conn:
        db_conn.execute(sqlalchemy.text(schema))
        db_conn.commit()

def main() -> None:
    """Initializes a connection pool and creates tables."""
    cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    credentials = service_account.Credentials.from_service_account_file(cred_path)
    connector = Connector(credentials=credentials)
    pool = init_connection_pool(connector)
    migrate_db(pool)
    print("Database initialized successfully.")
    connector.close()

if __name__ == "__main__":
    main()
