# ---------------------------------------------------------
# Stage 1 — Builder Image
# Installs dependencies in an isolated environment
# ---------------------------------------------------------
FROM python:3.11-slim AS builder

# Configure environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy dependency list first (optimizes Docker caching)
COPY requirements.txt .

# Install dependencies into a local directory
RUN pip install --user --no-cache-dir -r requirements.txt


# ---------------------------------------------------------
# Stage 2 — Runtime Image (Smaller, Secure, Non-Root)
# ---------------------------------------------------------
FROM python:3.11-slim AS runtime

# Create user & group (non-root)
RUN addgroup --system django && adduser --system --ingroup django django

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/django/.local/bin:${PATH}"

WORKDIR /app

# Copy installed Python libs from builder
COPY --from=builder /root/.local /home/django/.local

# Copy project code
COPY . .

# Change permissions so non-root user can access the app directory
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose Django port
EXPOSE 80
