#!/bin/sh

# Attendre que la DB OLTP soit prête (on teste sur une seule base, ça suffit)
echo "Attente de la base de données..."
until pg_isready -h db_postgres -p 5432 -U nico; do
  echo "Postgres est indisponible - attente..."
  sleep 2
done

echo "Base de données prête ! Lancement des migrations Alembic..."
# Applique les migrations sur les 3 bases automatiquement
alembic upgrade head

echo "Migrations terminées. Lancement de Gunicorn..."
exec gunicorn -b 0.0.0.0:8000 --workers=3 --threads=2 --timeout=60 --access-logfile=- --error-logfile=- "flask_app.main:app"