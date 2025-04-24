FROM python:3.13-rc-slim

WORKDIR /app

# Install system tools and uv package manager
RUN apt-get update && apt-get install -y gcc libffi-dev build-essential && \
    pip install --upgrade pip && pip install uv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy dependency definition file
COPY pyproject.toml ./

# Generate a pinned requirements.txt file from pyproject.toml
RUN uv pip compile --output-file requirements.txt pyproject.toml

# Install dependencies using uv
RUN uv pip install --system --requirement requirements.txt

# Copy the rest of the application code
COPY . .

EXPOSE 8501

# Launch command for the Streamlit application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
