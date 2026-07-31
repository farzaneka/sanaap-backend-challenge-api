#!/bin/sh
set -e

echo "Waiting for postgres..."
until pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-dms_user}" >/dev/null 2>&1; do
  sleep 1
done
echo "Postgres is up."

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
