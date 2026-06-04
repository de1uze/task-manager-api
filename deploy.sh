#!/usr/bin/env bash
# deploy.sh — rebuild and redeploy the task-manager-api container locally.
# Usage: ./deploy.sh

set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-task-manager-api:dev}"
CONTAINER_NAME="${CONTAINER_NAME:-task-manager-api}"
HOST_PORT="${HOST_PORT:-8000}"
HEALTH_URL="http://localhost:${HOST_PORT}/health"
HEALTH_TIMEOUT_SECONDS="${HEALTH_TIMEOUT_SECONDS:-30}"

# Pretty output (auto-disabled when stdout isn't a terminal).
if [[ -t 1 ]]; then
    BOLD=$'\033[1m'; GREEN=$'\033[0;32m'; RED=$'\033[0;31m'
    YELLOW=$'\033[0;33m'; BLUE=$'\033[0;34m'; RESET=$'\033[0m'
else
    BOLD=""; GREEN=""; RED=""; YELLOW=""; BLUE=""; RESET=""
fi

log()  { echo "${BLUE}[deploy]${RESET} $*"; }
ok()   { echo "${GREEN}[ ok  ]${RESET} $*"; }
warn() { echo "${YELLOW}[warn ]${RESET} $*"; }
fail() { echo "${RED}[fail ]${RESET} $*" >&2; }

# Sanity check.
if ! command -v docker >/dev/null 2>&1; then
    fail "docker not found in PATH"
    exit 1
fi
if ! docker info >/dev/null 2>&1; then
    fail "docker daemon is not running — start Docker Desktop and retry"
    exit 1
fi

# 1. Stop & remove old container if present.
if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
    log "stopping old container '${CONTAINER_NAME}'..."
    docker stop "${CONTAINER_NAME}" >/dev/null || true
    log "removing old container '${CONTAINER_NAME}'..."
    docker rm "${CONTAINER_NAME}" >/dev/null || true
else
    log "no existing container named '${CONTAINER_NAME}'"
fi

# 2. Build fresh image.
log "building image '${IMAGE_NAME}'..."
docker build -t "${IMAGE_NAME}" .
ok "image built"

# 3. Start new container.
log "starting new container on port ${HOST_PORT}..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${HOST_PORT}:8000" \
    --restart unless-stopped \
    "${IMAGE_NAME}" >/dev/null
ok "container started"

# 4. Poll /health.
log "waiting up to ${HEALTH_TIMEOUT_SECONDS}s for ${HEALTH_URL}..."
deadline=$(( $(date +%s) + HEALTH_TIMEOUT_SECONDS ))
while (( $(date +%s) < deadline )); do
    if curl -fsS "${HEALTH_URL}" >/dev/null 2>&1; then
        echo
        ok "${BOLD}deployment healthy${RESET}"
        echo "    ${HEALTH_URL} → $(curl -s ${HEALTH_URL})"
        echo "    swagger UI: http://localhost:${HOST_PORT}/docs"
        exit 0
    fi
    sleep 1
done

# 5. Failure path.
echo
fail "health check did not pass within ${HEALTH_TIMEOUT_SECONDS}s"
warn "container status:"
docker ps -a --filter "name=${CONTAINER_NAME}" --format \
    'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
warn "last 30 log lines:"
docker logs --tail 30 "${CONTAINER_NAME}" || true
exit 1
