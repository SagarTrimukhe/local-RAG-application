#!/bin/bash
set -e

OLLAMA_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"

echo "Waiting for Ollama at $OLLAMA_URL ..."
until curl -sf "$OLLAMA_URL/api/tags" > /dev/null 2>&1; do
  echo "  Ollama not ready yet – retrying in 3s"
  sleep 3
done
echo "Ollama is up."

# pull_model() {
#   local model="$1"
#   echo "Pulling model: $model ..."
#   curl -s "$OLLAMA_URL/api/pull" -d "{\"name\": \"$model\"}" | while IFS= read -r line; do
#     # Show progress status lines
#     status=$(echo "$line" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
#     [ -n "$status" ] && echo "  [$model] $status"
#   done
#   echo "Model $model ready."
# }

pull_model() {
  local model="$1"
  echo "Pulling model: $model ..."
  curl -s "$OLLAMA_URL/api/pull" -d "{\"name\": \"$model\"}"
  echo "Model $model ready."
}

pull_model "${LLM_MODEL:-llama3.2}"
pull_model "${EMBEDDING_MODEL:-nomic-embed-text}"

echo "All models pulled. Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 9000
