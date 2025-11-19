#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Initialize database if it doesn't exist
if [ ! -f notifi.db ]; then
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
fi
