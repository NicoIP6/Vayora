# Image légère officielle
FROM python:3.13-slim

# Sécurité + bonnes pratiques
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Créer un user non-root
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# AJOUT : postgresql-client pour pg_isready (indispensable pour l'orchestration)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Installer dépendances
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code ET les fichiers de migration
COPY shared ./shared
COPY flask_app ./flask_app
COPY migrations ./migrations
COPY alembic.ini .

# AJOUT : Copier le script de démarrage (entrypoint)
# On verra le contenu de ce script juste après
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Changer ownership
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# MODIFICATION : On utilise le script entrypoint au lieu de Gunicorn direct
ENTRYPOINT ["./entrypoint.sh"]