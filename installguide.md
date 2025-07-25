# SpotAxis Installation Guide

## Clone the repository

```bash
git clone https://github.com/Assystant/SpotAxis.git
```

Make sure you are cloning all the branches, not just the default develop branch

## Change the active directory to `SpotAxis`

```bash
cd SpotAxis
```

## Even though this is the default branch, still make sure that you are on the `develop` branch

```bash
git checkout develop
```

## Install MySQL and create a database

```bash
https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/
```

## Install `uv` if you havent already installed it on your system

```bash
https://docs.astral.sh/uv/getting-started/installation/
```

## Set up the `uv` environment

- Create a virtual environment

    ```bash
    uv venv
    ```

- Install all the dependencies

    ```bash
    uv pip install -r pyproject.toml
    ```

- Tip: if you want to add more dependencies to the project

    ```bash
    uv add <package-name>
    ```

## Update the `setup/config.json` with appropriate email and database credentials

```json
{
  "env_type": "local_development",
  "db_creds": {
    "db_name": "TRM_local",
    "db_user": "TRM_user",
    "db_password": "pass",
    "db_host": "",
    "db_port": ""
  },
  "email_creds": {
    "email_host_user": "contact.travelder@gmail.com",
    "email_host_password": "qwerty123$",
    "email_port": "587"
  }
}
```

## Run the `install.py` script:  or, Follow the interactive prompt to enter the email and db credentials

```bash
py install.py -f setup/config.json
```

Or, Follow the interactive prompt to enter the email and db credentials.
