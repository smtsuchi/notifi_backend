#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
# Initialize migrations directory if it doesn't exist
if [ ! -d "migrations" ]; then
    flask db init
fi

# Create and apply migrations
flask db migrate -m "Auto migration on deployment" || true
flask db upgrade
