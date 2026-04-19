#!/bin/sh
set -e

if [ -f .env ]; then
    echo ".env already exists, skipping setup."
    exit 0
fi

cp .env.example .env

JWT_SECRET=$(openssl rand -hex 32)

if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s/change-me-to-a-long-random-string/$JWT_SECRET/" .env
else
    sed -i "s/change-me-to-a-long-random-string/$JWT_SECRET/" .env
fi

echo ".env created with a random JWT secret."
