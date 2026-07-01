#!/bin/bash
set -euo pipefail
PT_TOKEN=$(cat /tmp/token_b64.txt | tr -d '\n' | base64 -d)
ENDPOINT="http://192.168.1.19:9001"
echo "📋 Token OK: ${PT_TOKEN:0:6}...${PT_TOKEN: -4}"
echo "🚀 Étape 1: Suppression ancien conteneur..."
curl -s -X DELETE "${ENDPOINT}/api/endpoints/2/docker/containers/sf-overlay2?force=true" \
  -H "x-api-key: ${PT_TOKEN}" || true
echo ""
echo "🚀 Étape 2: Rebuild de l'image..."
cd /opt/data/sf-overlay2
tar czf /tmp/sf-overlay2.tar.gz \
  --exclude=.venv --exclude=__pycache__ --exclude='*.pyc' --exclude='egg-info' \
  Dockerfile pyproject.toml app/ 2>/dev/null
curl -s -X POST \
  "${ENDPOINT}/api/endpoints/2/docker/build?t=sf-overlay2:latest&dockerfile=Dockerfile&rm=1" \
  -H "x-api-key: ${PT_TOKEN}" \
  -H "Content-Type: application/x-tar" \
  --data-binary @/tmp/sf-overlay2.tar.gz | grep -E '(Successfully|error)' || true
echo ""
echo "🚀 Étape 3: Création du conteneur sur port 8002..."
CID=$(curl -s -X POST \
  "${ENDPOINT}/api/endpoints/2/docker/containers/create?name=sf-overlay2" \
  -H "x-api-key: ${PT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "sf-overlay2:latest",
    "HostConfig": {
      "PortBindings": {"8000/tcp": [{"HostPort": "8002"}]},
      "RestartPolicy": {"Name": "unless-stopped"}
    }
  }' | python3 -c "import sys,json; print(json.load(sys.stdin).get('Id','NO_ID'))")
echo "   ID: ${CID:0:20}..."
if [ "$CID" != "NO_ID" ]; then
  echo "▶️  Démarrage..."
  curl -s -X POST "${ENDPOINT}/api/endpoints/2/docker/containers/${CID}/start" \
    -H "x-api-key: ${PT_TOKEN}"
  echo ""
  echo "========================================="
  echo "  ✅ SF-OVERLAY2 DÉPLOYÉ !"
  echo "========================================="
  echo "  🌐 http://192.168.1.19:8002"
  echo "========================================="
fi
