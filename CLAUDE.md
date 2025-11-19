# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NotiFi is an automated price drop notification application that tracks Amazon product prices and notifies users via email when prices change. Built with Flask/Python backend, SQLite database (development), and web scraping using BeautifulSoup.

## Environment Setup

### Python Version
This project uses **Python 3.13** (specified in `.python-version`).

### Database
Uses **SQLite** for development (file: `notifi.db`). The database file is created automatically when you run migrations. For production, set the `DATABASE_URL` environment variable to a PostgreSQL connection string (requires adding `psycopg2-binary` to requirements.txt).

### Required Environment Variables (.env)
```
FLASK_APP=run.py
FLASK_DEBUG=True  # Set to False in production
SECRET_KEY=<random-string>
# DATABASE_URL is optional - defaults to sqlite:///notifi.db
# For production PostgreSQL: DATABASE_URL=postgresql://user:password@host:port/dbname
FRONTEND_URL=<frontend-url>  # Usually http://localhost:5173 for local dev
GOOGLE_APP_PASSWORD=<app-password-from-google>
GOOGLE_EMAIL_SENDER=<gmail-address>
```

### Installation
```bash
# MacOS/Linux
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows (ensure Python 3.13 is installed)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Note**: The `.python-version` file tells cloud platforms like Render to use Python 3.13.

### Database Initialization
Run once when setting up the database (creates `notifi.db` SQLite file):
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

The SQLite database file (`notifi.db`) will be created in the project root. It's automatically excluded from git via `.gitignore`.

### Running the Server
```bash
flask run
```

## Architecture

### Core Components

**Flask Application (`app/__init__.py`)**: Initializes Flask app with extensions:
- SQLAlchemy for database ORM
- Flask-Migrate for database migrations
- Flask-JWT-Extended for JWT authentication with cookie/header support
- Flask-CORS for cross-origin requests
- APScheduler for scheduled tasks (web scraping every 30 minutes)

**Database Models (`app/models.py`)**:
- `User`: Stores user credentials, notification preferences (`notification_method`, `notify_on_drop_only`)
- `Product`: Amazon product details with relationships to prices and subscribers
- `Price`: Historical price records for products
- `Subscription`: Many-to-many relationship between users and products
- `Log`: Notification history for auditing

**Authentication (`app/auth/`)**:
- JWT-based authentication with 1-hour access token expiration
- Basic HTTP auth for login endpoint (`wrappers.py`)
- Case-insensitive username/email lookups
- Password hashing with Werkzeug

**API Routes (`app/api/routes.py`)**:
- `/subscribe`: Creates subscription and scrapes product details on-demand
- `/unsubscribe`: Soft-deletes subscription by setting `cancelled_date`
- `/subscriptions`: Returns user's active subscriptions
- `/user/notification-method`: Updates email/sms/both preference
- `/user/notify-on-drop-only`: Toggle to only notify on price drops
- `/products/prices/<product_id>`: Get price history for charts
- `/send/emails`: Manual trigger for scraping/notifications

**Scheduled Tasks (`app/scheduled_tasks/tasks.py`)**:
- `scrape_products()`: Runs every 30 minutes via APScheduler
- Scrapes all products in database, creates new Price records
- Triggers notifications if price changed

**Web Scraping (`app/helpers/web_scrapers.py`)**:
- BeautifulSoup-based Amazon scraper
- Extracts: product name, price (handles multiple price element formats), image URL, description
- Returns error dict if scraping fails

**Notifications (`app/helpers/send_notifications.py`)**:
- SMTP email via Gmail (active)
- SMS via Twilio (commented out - blocked by A2P 10DLC regulations)
- Respects user's `notify_on_drop_only` preference
- Creates Log entries for sent notifications

### Key Patterns

**UUID-based IDs**: Products use `prod_` prefix, Subscriptions use `sub_` prefix
**Soft Deletes**: Subscriptions set `cancelled_date` instead of deletion
**Price History**: Price changes tracked in separate Price table for charting
**Eager vs Lazy Loading**: Relationships use `lazy='dynamic'` for query flexibility

### Important Business Logic

**Subscription Flow**:
1. User subscribes to Amazon URL
2. Product scraped (or existing product updated)
3. Initial Price record created
4. Subscription record created (or reactivated if previously cancelled)

**Notification Logic** (`send_notifications()` in send_notifications.py:83):
- Filters subscribers based on `notify_on_drop_only` setting
- Skips notification if price increased and user wants drop-only alerts
- Groups subscribers by notification method (email/sms/both)

**Case Sensitivity**: Username and email are converted to lowercase on signup/login (auth/routes.py:11-13)

### Testing

Basic unit tests use Python's `unittest` framework (though test files are not present in current repository state).

## Common Development Tasks

### Database Migrations
```bash
flask db migrate -m "description"
flask db upgrade
```

### Manual Price Check/Notification Trigger
POST to `/send/emails` endpoint (no auth required in current implementation)
