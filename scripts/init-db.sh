#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h postgres -p 5432 -U timly; do
  echo "Waiting for PostgreSQL to start..."
  sleep 2
done

# Run database migrations
alembic upgrade head

# Optional: Seed initial data
# psql -U timly -d timly_dev -f /app/scripts/seed.sql
