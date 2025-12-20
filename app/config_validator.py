"""
Configuration validation and application startup guard.
"""

import os
import sys
from typing import List
from app.core.config import Config


def validate_config(config: Config) -> List[str]:
    """
    Validate the configuration and return a list of validation errors.

    Args:
        config: The application configuration instance

    Returns:
        List of error messages, empty if no errors
    """
    errors = []

    # Check if .env file exists
    if not os.path.exists(".env"):
        errors.append(
            "Environment file (.env) not found. Please create it based on .env.example"
        )

    # Check required fields (these will be empty strings if not provided)
    if not config.db_user:
        errors.append("DB_USER is required but not provided")
    if not config.db_password:
        errors.append("DB_PASSWORD is required but not provided")
    if not config.db_host:
        errors.append("DB_HOST is required but not provided")
    if not config.db_port:
        errors.append("DB_PORT is required but not provided")
    if not config.db_name:
        errors.append("DB_NAME is required but not provided")
    if not config.secret_key or len(config.secret_key) < 32:
        errors.append(
            "SECRET_KEY must be exist and at least 32 characters long for security"
        )

    return errors


def ensure_valid_config() -> Config:
    """
    Create and validate configuration, exiting the application if validation fails.

    Returns:
        Validated Config instance

    Exits:
        If configuration validation fails, prints error message and exits with code 1
    """
    try:
        config = Config()
    except Exception:
        # Check if the error is due to missing .env file by checking if file exists
        if not os.path.exists(".env"):
            print(
                "Configuration error: Required environment variables are not set.",
                file=sys.stderr,
            )
            print(
                "\nPlease create a .env file based on .env.example or set the environment variables directly.",
                file=sys.stderr,
            )
            print(
                "Required variables: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME",
                file=sys.stderr,
            )
        else:
            print(
                "Configuration error: Some required environment variables are missing or invalid.",
                file=sys.stderr,
            )
            print(
                "\nPlease check your .env file or environment variables.",
                file=sys.stderr,
            )
            print(
                "Required variables: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME",
                file=sys.stderr,
            )
        sys.exit(1)

    errors = validate_config(config)

    if errors:
        print("Configuration validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(
            "\nPlease ensure all required environment variables are set.",
            file=sys.stderr,
        )
        print("You can create a .env file based on .env.example", file=sys.stderr)
        sys.exit(1)

    return config
