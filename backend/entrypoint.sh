#!/bin/bash

echo "Starting entrypoint script..."

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations automatically in dev
if [ "$DJANGO_ENV" = "dev" ]
then
    echo "Running migrations for development..."
    python manage.py migrate
    echo "Migrations complete"
fi

echo "Executing command: $@"
exec "$@"