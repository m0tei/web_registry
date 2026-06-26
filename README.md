# Web Registry

A web-based document registry system built for schools to manage and track incoming/outgoing documents chronologically. Built with Flask, MongoDB, and real-time updates via WebSockets.

---

## What It Does

The app acts as a digital replacement for a physical document registry book (*registru*). Staff can log documents — letters, requests, decisions — with metadata like origin, content summary, recipient department, and dispatch date. Every entry is auto-numbered sequentially, and the system enforces chronological ordering so the registry remains legally valid.

**Two roles:**
- **Admin** — full access: add, edit, delete entries, manage users, download yearly exports
- **User** — read-only view of their own submitted entries

---

## Features

- **Document logging** — register incoming/outgoing documents with full metadata (document number, origin, content summary, assigned department, dispatch date, recipient)
- **Chronological integrity** — entries are validated to ensure dates don't break the sequential order of the registry
- **Year-based collections** — each calendar year is stored as a separate MongoDB collection; past years remain accessible
- **Real-time updates** — table updates live via Flask-SocketIO without page reloads
- **Excel export** — download any year's registry as a formatted `.xlsx` file
- **User management** — admins can activate/deactivate user accounts
- **Mongo Express** — bundled database UI for direct DB inspection (port 8081)
- **Automated backups** — a dedicated backup container snapshots the database daily (configurable via cron)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database | MongoDB 5.0 |
| Real-time | Flask-SocketIO (WebSockets via eventlet) |
| Auth | Flask-Login (session-based) |
| Frontend | Jinja2 templates |
| Export | openpyxl |
| Server | Gunicorn |
| Deployment | Docker Compose |

---

## Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose

### Run

```bash
git clone <repo-url>
cd web_registry

# Copy and configure environment
cp .env.example .env  # edit credentials if needed

docker compose up -d
```

The app will be available at **http://localhost:5000**.  
Mongo Express (DB admin UI) runs at **http://localhost:8081**.

### Services started by Docker Compose

| Service | Description | Port |
|---|---|---|
| `web_app` | Flask application | 5000 |
| `mongo` | MongoDB database | — (internal) |
| `mongo_express` | MongoDB admin UI | 8081 |
| `mongo_backup` | Automated daily backups | — |

---

## Environment Variables

Configure these in your `.env` file:

```env
DEBUG=False
SECRET_KEY=your-secret-key

MONGO_DB_HOST=mongo_db
MONGO_DB_USER=your_db_user
MONGO_DB_PASS=your_db_password
```

> **Note:** The default credentials in `.env` are for local development only. Change them before any production deployment.

---

## API Endpoints

All endpoints require authentication.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/index` | Admin dashboard |
| `GET` | `/user` | User dashboard |
| `POST` | `/api/entry/add` | Add or update a registry entry |
| `GET` | `/api/table/show` | Paginated entries for current year |
| `GET` | `/api/table/show/<user_id>` | Entries filtered by user |
| `GET` | `/api/table/next` | Next available entry ID |
| `DELETE` | `/api/table/del/<id>` | Delete an entry |
| `GET` | `/api/table/collections` | List all available years |
| `GET` | `/api/table/download/<year>` | Download year as `.xlsx` |
| `GET` | `/api/users/show` | List all users |
| `GET` | `/api/users/switchstatus/<id>` | Toggle user active/inactive |

---

## Project Structure

```
web_registry/
├── apps/
│   ├── __init__.py              # App factory, blueprint + extension registration
│   ├── config.py                # Config classes, MongoDB connection
│   ├── authentication/          # Login, register, user model
│   └── home/
│       ├── routes.py            # Main app routes and API endpoints
│       └── util.py              # Date formatting helpers
├── docker-compose.yml
├── Dockerfile
├── gunicorn-cfg.py
├── requirements.txt
└── run.py
```

---

## Backup

The `mongo_backup` container runs a daily snapshot at midnight (Romania time) and keeps the last 5 backups. Configure via environment variables:

```env
MONGO_DB_NUM=5          # number of backups to retain
CRON_TIME=0 0 * * *     # cron schedule
```

Backups are stored in the `db_backup` Docker volume.
