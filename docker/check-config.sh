#!/bin/bash

# Script to automatically set up Docker Compose override for local AskAI config and private patterns

USER_CONFIG="$HOME/.askai/config.yml"
OVERRIDE_FILE="docker-compose.override.yml"

# Remove existing override file
if [ -f "$OVERRIDE_FILE" ]; then
    rm "$OVERRIDE_FILE"
fi

# Check for private patterns directory from config
PRIVATE_PATTERNS_PATH=""
if [ -f "$USER_CONFIG" ]; then
    # Extract private patterns path from config (handle various YAML formats)
    PRIVATE_PATTERNS_PATH=$(grep -E "^\s*private_patterns_path:" "$USER_CONFIG" | sed 's/.*private_patterns_path:\s*//' | sed 's/["'"'"']//g' | xargs)
    # Expand ~ to home directory if needed
    if [[ "$PRIVATE_PATTERNS_PATH" == "~"* ]]; then
        PRIVATE_PATTERNS_PATH="${PRIVATE_PATTERNS_PATH/#\~/$HOME}"
    fi
fi

if [ -f "$USER_CONFIG" ]; then
    echo "✓ Found local AskAI config at $USER_CONFIG"

    # Check for private patterns
    if [ -n "$PRIVATE_PATTERNS_PATH" ] && [ -d "$PRIVATE_PATTERNS_PATH" ]; then
        echo "✓ Found private patterns directory at $PRIVATE_PATTERNS_PATH"
        echo "✓ Creating docker-compose.override.yml to copy config and private patterns"

        cat > "$OVERRIDE_FILE" << EOF
# Auto-generated override to use local AskAI config and private patterns
services:
  askai-api:
    volumes:
      - \${HOME}/.askai/config.yml:/tmp/host-config.yml:ro
      - $PRIVATE_PATTERNS_PATH:/app/private-patterns:ro
EOF
    else
        echo "ℹ  No private patterns directory found or configured"
        echo "✓ Creating docker-compose.override.yml to mount config only"

        cat > "$OVERRIDE_FILE" << EOF
# Auto-generated override to use local AskAI config
services:
  askai-api:
    volumes:
      - \${HOME}/.askai/config.yml:/tmp/host-config.yml:ro
EOF
    fi

    echo "✓ Override file created. Your local config will be used in the container."
    if [ -n "$PRIVATE_PATTERNS_PATH" ] && [ -d "$PRIVATE_PATTERNS_PATH" ]; then
        echo "✓ Private patterns will be available in the container at /app/private-patterns"
    fi
else
    echo "ℹ  No local AskAI config found at $USER_CONFIG"
    echo "ℹ  Container will create default configuration using environment variables"
    echo "ℹ  Set API_KEY environment variable or run 'askai config' locally first"
fi

echo ""
echo "Starting Docker container..."
exec docker compose "$@"