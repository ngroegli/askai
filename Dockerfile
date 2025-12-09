# Multi-stage Docker build for AskAI API
FROM python:3.12-alpine as base

LABEL version="1.2.1"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=askai.presentation.api.app:create_app \
    FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=8080 \
    API_KEY="" \
    DEFAULT_MODEL="gpt-3.5-turbo" \
    BASE_URL="https://openrouter.ai/api/v1"

# Install system dependencies for Alpine
RUN apk update && apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    curl \
    && rm -rf /var/cache/apk/*

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY src/askai/presentation/api/requirements.txt /app/api-requirements.txt
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r api-requirements.txt

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/
COPY patterns/ /app/patterns/
COPY pyproject.toml /app/
COPY README.md /app/

# Install the package in development mode
RUN cd /app && pip install -e .

# Create non-root user (Alpine syntax)
RUN adduser -D -s /bin/sh askai && \
    chown -R askai:askai /app

# Switch to non-root user
USER askai

# Create AskAI directory structure and config for non-interactive startup
RUN mkdir -p /home/askai/.askai/chats && \
    mkdir -p /app/logs && \
    mkdir -p /app/private-patterns

# Create a startup script that checks for mounted config and sets up private patterns
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'if [ -f /tmp/host-config.yml ]; then' >> /app/start.sh && \
    echo '  echo "Using host config file from ~/.askai/config.yml"' >> /app/start.sh && \
    echo '  cp /tmp/host-config.yml /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo '  # Update private patterns path to use container location' >> /app/start.sh && \
    echo '  sed -i "s|private_patterns_path:.*|private_patterns_path: /app/private-patterns|g" /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo 'elif [ ! -f /home/askai/.askai/config.yml ]; then' >> /app/start.sh && \
    echo '  echo "Creating default config file"' >> /app/start.sh && \
    echo '  echo "api_key: ${API_KEY:-dummy-key}" > /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo '  echo "default_model: ${DEFAULT_MODEL:-gpt-3.5-turbo}" >> /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo '  echo "base_url: ${BASE_URL:-https://openrouter.ai/api/v1}" >> /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo '  echo "enable_logging: true" >> /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo '  echo "log_level: INFO" >> /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo '  echo "log_path: /app/logs/askai.log" >> /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo '  echo "patterns:" >> /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo '  echo "  private_patterns_path: /app/private-patterns" >> /home/askai/.askai/config.yml' >> /app/start.sh && \
    echo 'else' >> /app/start.sh && \
    echo '  echo "Using existing config file"' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo 'exec "$@"' >> /app/start.sh && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health/live || exit 1

# Set Python path to include src directory
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Run the application with explicit working directory
ENTRYPOINT ["/app/start.sh"]
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "askai.presentation.api.app:create_app()"]