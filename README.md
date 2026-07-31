# Sanaap DMS API — Document Management System

A Django REST Framework backend for securely uploading, storing, retrieving
and managing documents, with role based access control (RBAC), object
storage on MinIO, background processing, real-time WebSocket notifications,
and full API documentation via Swagger/OpenAPI.

## Features

| Requirement | Implementation |
|---|---|
| Upload / update / retrieve / delete documents | `apps/documents` — `DocumentViewSet` (DRF `ModelViewSet`) |
| Object storage | MinIO via `django-storages` (`apps/documents/storage.py`) |
| Auth | Django's built-in username/password auth model, exposed via JWT (`djangorestframework-simplejwt`) |
| RBAC (admin / editor / viewer) | `apps/documents/permissions.py`, `apps/users/permissions.py` |
| Secure document URLs | Presigned, time-limited S3/MinIO URLs (`AWS_QUERYSTRING_AUTH`) |
| Filtering & pagination | `django-filter` + DRF `PageNumberPagination` |
| SOLID principles | See [Design notes](#design-notes) below |
| Unit tests | `pytest` + `pytest-django` + `factory_boy`, in `tests/` |
| API docs | `drf-spectacular` (Swagger UI at `/api/docs/`) |
| Docker | `Dockerfile` + `docker-compose.yml` (Django, PostgreSQL, Redis, MinIO) |
| Background processing | Celery worker (`apps/documents/tasks.py`) |
| Audit logging | `apps/audit` — middleware + model signals |
| Reverse proxy | Nginx (`nginx/nginx.conf`) in front of Gunicorn + Daphne |
| Real-time notifications | Django Channels WebSocket (`apps/documents/consumers.py`) |

## Roles (RBAC)

| Role | Create user / assign role | Upload / update document | Delete document | View documents |
|---|---|---|---|---|
| `admin` | ✅ | ✅ (any document) | ✅ | ✅ (all documents) |
| `editor` | ❌ | ✅ (own documents) | ❌ | ✅ (own documents) |
| `viewer` | ❌ | ❌ | ❌ | ✅ (own documents) |

Admins see and manage every document; editors and viewers are scoped to
their own uploads (`DocumentViewSet.get_queryset`).

## API Overview

All endpoints are prefixed with `/api/`.

- `POST /api/auth/login/` — obtain JWT access/refresh token pair (username + password)
- `POST /api/auth/refresh/` — refresh an access token
- `GET/POST /api/users/` — list users / create a user (admin only for POST)
- `GET /api/users/me/` — current user's profile
- `PATCH /api/users/<id>/role/` — change a user's role (admin only)
- `GET/POST /api/documents/` — list (filtered & paginated) / upload a document
- `GET/PUT/PATCH/DELETE /api/documents/<id>/` — retrieve / update / delete a document
- `GET /api/docs/` — Swagger UI
- `GET /api/redoc/` — ReDoc UI
- `GET /api/schema/` — raw OpenAPI schema
- `ws://<host>/ws/documents/` — WebSocket, broadcasts `document_processed` events

### Filtering & search on `GET /api/documents/`

`?title=<icontains>` · `?tags=<icontains>` · `?content_type=<iexact>` ·
`?owner=<user id>` · `?created_after=<date>` · `?created_before=<date>` ·
`?search=<title/description/tags>` · `?ordering=created_at|title|size` ·
`?page=<n>`

## Local Development (Docker — recommended)

```bash
cp .env.example .env
# edit .env and set real secrets before any non-local use

docker compose up --build
```

This brings up:
- `web` — Django app served by Gunicorn (behind Nginx)
- `websocket` — Django Channels app served by Daphne (behind Nginx, path `/ws/`)
- `celery_worker` — background task processor
- `db` — PostgreSQL 16
- `redis` — cache, Celery broker, and Channels layer
- `minio` + `minio-init` — S3-compatible object storage, with the bucket auto-created
- `nginx` — reverse proxy on port 80

Migrations run automatically on container start via `entrypoint.sh`.

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

Then visit:
- `http://localhost/api/docs/` — Swagger UI
- `http://localhost/admin/` — Django admin
- `http://localhost:9001` — MinIO console (credentials from `.env`)

## Local Development (without Docker)

You'll need PostgreSQL, Redis, and a running MinIO instance locally.

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # point POSTGRES_HOST/REDIS_URL/MINIO_ENDPOINT_URL at localhost
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Run the Celery worker and Channels server in separate terminals if you need
background processing / WebSocket notifications locally:

```bash
celery -A config worker --loglevel=info
daphne -b 0.0.0.0 -p 8001 config.asgi:application
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Tests use `pytest-django` with `--reuse-db`, `factory_boy` for fixtures, and
swap the storage backend to the local filesystem (see `tests/conftest.py`)
so a live MinIO instance isn't required to run the suite.

Test coverage includes:
- RBAC enforcement per role, per HTTP method (`tests/test_document_permissions.py`)
- Filtering, search, and pagination (`tests/test_document_filtering.py`)
- User creation and role assignment (`tests/test_user_management.py`)

## Design Notes

**SOLID principles applied:**

- **Single Responsibility** — permissions, serializers, filters, storage,
  and background tasks each live in their own module per app, rather than
  being crammed into `views.py`.
- **Open/Closed** — `MinioMediaStorage` subclasses `S3Boto3Storage` so
  storage behaviour can be extended (e.g. custom key naming) without
  modifying `django-storages` or scattering S3 configuration through the
  codebase. `DocumentPermission` / `IsAdmin` are composable permission
  classes that can be combined for new endpoints without rewriting
  role-checking logic.
- **Liskov Substitution** — `User` extends Django's `AbstractUser`, so it
  remains fully compatible with any code (admin, auth backends,
  `contrib.auth`) that expects a standard Django user.
- **Interface Segregation** — serializers are split by intent
  (`UserSerializer` for reads, `UserCreateSerializer` for admin-only
  creation, `UserRoleUpdateSerializer` for role changes) instead of one
  serializer trying to handle every case with conditional logic.
- **Dependency Inversion** — views depend on the `DocumentPermission`
  abstraction and the storage abstraction (`settings.STORAGES`), not on
  concrete MinIO/S3 details; the storage backend is swapped for local
  filesystem storage in tests without touching any application code.

**Security:**
- Document URLs are never served directly from MinIO's public path — 
  `AWS_QUERYSTRING_AUTH` generates short-lived, signed URLs
  (`MINIO_PRESIGNED_URL_EXPIRE_SECONDS`, default 5 minutes).
- File uploads are validated for both size (`MAX_UPLOAD_SIZE_BYTES`) and
  content type (`ALLOWED_UPLOAD_CONTENT_TYPES`) before being persisted.
  Storage keys are derived from the document's UUID rather than the
  user-supplied filename, preventing path traversal / collisions.
  Encryption/HTTPS for MinIO can be enabled via `MINIO_USE_SSL=True`.
- JWT access tokens are short-lived (30 min) with rotating, blacklisted
  refresh tokens.

## Project Layout

```
.
├── config/                # Django project settings, URLs, Celery, ASGI/WSGI
├── apps/
│   ├── users/              # Custom User model, RBAC roles, user admin endpoints
│   ├── documents/          # Document model, upload/CRUD API, MinIO storage,
│   │                       # Celery tasks, Channels consumer/routing
│   └── audit/               # Audit log model, request-logging middleware
├── tests/                 # pytest test suite + factories
├── nginx/nginx.conf        # Reverse proxy config
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh           # Waits for DB, runs migrations, collects static
├── requirements.txt / requirements-dev.txt
└── .env.example
```

## Git Flow

This repository follows Git Flow:

- `main` — production-ready releases.
- `develop` — integration branch.
- `feature/*` — one branch per feature (users/RBAC, document CRUD, MinIO
  storage, filtering & pagination, Celery/audit/Channels/Nginx bonus
  features, tests & docs), merged into `develop` via PR, then released to
  `main`.

## Notes on Reproducing Migrations

The initial migrations under `apps/*/migrations/0001_initial.py` were
authored by hand to match the models exactly, since this environment could
not reach PyPI to install Django and run `makemigrations` directly. If you
change any model, regenerate migrations the normal way:

```bash
python manage.py makemigrations
```

## Additional Challenges Implemented

- ✅ Celery background task processing for documents (`apps/documents/tasks.py`)
- ✅ Audit logging for document access and changes (`apps/audit`)
- ✅ Nginx reverse proxy (`nginx/nginx.conf`)
- ✅ Django Channels WebSocket notifications on document create/update
  (`apps/documents/consumers.py`, broadcast to all connected users)
