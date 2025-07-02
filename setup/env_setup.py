# setup/env_setup.py

import re
from pathlib import Path
from dotenv import dotenv_values
from django.core.management.utils import get_random_secret_key

TEMPLATE_FILE = 'setup/env_template.txt'
OUTPUT_FILE = '.env'


def is_boolean(value):
    return value.lower() in {'true', 'false'}


def is_numeric(value):
    return re.fullmatch(r'\d+', value) is not None


def prompt_environment():
    print("Select environment setup:")
    print("1. Local Development")
    print("2. Server Development")
    print("3. Production Deployment")

    while True:
        choice = input("Enter choice [1-3]: ").strip()
        match choice:
            case '1':
                return 'local_development'
            case '2':
                return 'server_development'
            case '3':
                return 'productive'
            case _:
                print("Invalid input. Please choose 1, 2, or 3.")


def prompt_db_credentials():
    print("\nEnter your database credentials:")
    db_name = input("Database Name: ").strip()
    db_user = input("Database User: ").strip()
    db_pass = input("Database Password: ").strip()
    db_host = input("Database Host [default: localhost]: ").strip()
    db_port = input("Database Port [default: 3306]: ").strip()

    return {
        "db_name": db_name,
        "db_user": db_user,
        "db_password": db_pass,
        "db_host": db_host,
        "db_port": db_port,
    }


def prompt_email_credentials():
    print("\nEnter your email credentials:")
    email_user = input("Email User: ").strip()
    email_pass = input("Email Password: ").strip()
    email_port = input("Email Port: ").strip()

    return {
        "email_host_user": email_user,
        "email_host_password": email_pass,
        "email_port": email_port,
    }


def create_env_file(env_type, db_creds, email_creds, secret_key):
    if not Path(TEMPLATE_FILE).exists():
        print(f"Error: Template file '{TEMPLATE_FILE}' not found.")
        return

    env_dict = dotenv_values(TEMPLATE_FILE)
    env_dict['SECRET_KEY'] = secret_key
    env_dict['ENVIRONMENT'] = env_type
    env_dict.update(db_creds)
    env_dict.update(email_creds)

    with open(OUTPUT_FILE, 'w') as f:
        for key, value in env_dict.items():
            if is_numeric(value) or is_boolean(value):
                f.write(f"{key}={value}\n")
            else:
                f.write(f"{key}='{value}'\n")

    print(f"\n'.env' file created/updated successfully with {env_type} settings.")