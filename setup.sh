#!/bin/sh
set -e

RESTCOUNTRIES_API_KEY=""

for arg in "$@"; do
    case "$arg" in
        --key=*) RESTCOUNTRIES_API_KEY="${arg#--key=}" ;;
    esac
done

if [ -z "$RESTCOUNTRIES_API_KEY" ]; then
    echo "Usage: ./setup.sh --key=<restcountries-api-key>"
    exit 1
fi

if [ -f .env ]; then
    echo ".env already exists, skipping setup."
    exit 0
fi

cp .env.example .env

JWT_SECRET=$(openssl rand -hex 32)

if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s/change-me-to-a-long-random-string/$JWT_SECRET/" .env
    sed -i '' "s/your-api-key-here/$RESTCOUNTRIES_API_KEY/" .env
else
    sed -i "s/change-me-to-a-long-random-string/$JWT_SECRET/" .env
    sed -i "s/your-api-key-here/$RESTCOUNTRIES_API_KEY/" .env
fi

echo ".env created with a random JWT secret and restcountries API key."