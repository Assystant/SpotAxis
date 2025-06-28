
from setup.env_setup import (
    prompt_environment,
    prompt_db_credentials,
    prompt_email_credentials,
    create_env_file,
)
from django.core.management.utils import get_random_secret_key
import argparse
import json
from pathlib import Path

def load_config_from_file(path):
    if not Path(path).exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, 'r') as f:
        config = json.load(f)

    required_keys = {"env_type", "db_creds", "email_creds"}
    if not required_keys.issubset(config.keys()):
        raise ValueError(f"Config file must include keys: {required_keys}")
    return config["env_type"], config["db_creds"], config["email_creds"]

def main():
    parser = argparse.ArgumentParser(description="Setup environment from prompt or config file")
    parser.add_argument('-f', '--file', type=str, help='Path to JSON config file')

    args = parser.parse_args()

    print("Environment Setup Script\n")

    if args.file:
        try:
            env_type, db_creds, email_creds = load_config_from_file(args.file)
        except Exception as e:
            print(f"Error: {e}")
            return
    else:
        env_type = prompt_environment()
        db_creds = prompt_db_credentials()
        email_creds = prompt_email_credentials()

    secret_key = get_random_secret_key()
    create_env_file(env_type, db_creds, email_creds, secret_key)


if __name__ == '__main__':
    main()