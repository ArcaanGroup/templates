#!/usr/bin/env python3
"""
Script to ensure database exists for the FastAPI application.
This script will create the database if it doesn't exist.
"""

import sys
from pathlib import Path
from urllib.parse import quote_plus

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

from sqlalchemy import create_engine, text

from app.core.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    config = Config()

    # Connect to default postgres database to create our target database
    default_db_url = f"postgresql+asyncpg://{config.db_user}:{quote_plus(config.db_password)}@{config.db_host}:{config.db_port}/postgres"

    # Create sync engine to connect to default postgres DB
    # Using psycopg2 sync driver to create database (async driver can't create DB)
    sync_engine = create_engine(default_db_url.replace("asyncpg", "psycopg2"))

    try:
        with sync_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_catalog.pg_database WHERE datname = :db_name"),
                {"db_name": config.db_name},
            )

            database_exists = result.scalar() is not None

            if not database_exists:
                # Need to commit the current transaction before creating database
                conn.execute(text("COMMIT"))
                # Create the database
                conn.execute(text(f'CREATE DATABASE "{config.db_name}"'))
                conn.execute(text("COMMIT"))
                logger.info(f"Database '{config.db_name}' created successfully!")
            else:
                logger.info(f"Database '{config.db_name}' already exists.")
    finally:
        sync_engine.dispose()


def main():
    """Main function to run the database creation script."""
    logger.info("Starting database creation process...")

    # Create the database if it doesn't exist
    create_database_if_not_exists()

    logger.info("Database creation process completed!")


if __name__ == "__main__":
    main()
