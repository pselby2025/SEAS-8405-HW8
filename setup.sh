#!/bin/bash
set -e

echo "[*] Starting Docker containers..."
docker compose up -d --build

echo "[*] Waiting for Keycloak to be ready..."
until curl -s http://localhost:8080/realms/master > /dev/null; do
    echo "  ...waiting"
    sleep 5
done

echo "[*] Logging into Keycloak..."
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8080/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r .access_token)

echo "[*] Creating realm..."
curl -s -X POST "http://localhost:8080/admin/realms" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d @realm-config.json || echo "Realm may already exist."

echo "[✔] Setup complete!"