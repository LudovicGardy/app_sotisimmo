# Utiliser une image Python compatible
FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Installer uv (avec curl)
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://astral.sh/uv/install.sh | sh && \
    ln -s ~/.cargo/bin/uv /usr/local/bin/uv

# Copier le fichier de configuration du projet
COPY pyproject.toml ./

# Installer les dépendances avec uv
RUN uv pip install --system -e .

# Copier le reste du code de l'application
COPY . .

# Exposer le port de Streamlit
EXPOSE 8501

# Lancer l'application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
