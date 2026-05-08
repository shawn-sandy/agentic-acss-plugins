#!/bin/bash

set -euo pipefail

# Hot-reload server for the test sandbox.
# Watches SCSS and HTML files, recompiles CSS, and injects live-reload via esbuild's SSE.
#
# Usage:
#   tests/serve.sh
#
# Requirements:
#   - tests/sandbox/ exists (run `tests/setup.sh` if not)
#   - npm --prefix tests ci has been run
#   - Port 7743 is free (or will auto-increment to 7744, etc.)

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SANDBOX="$REPO_ROOT/tests/sandbox"

# --- Guards ---

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "Not a git repository." >&2
  exit 1
fi

if [[ ! -d "$SANDBOX" ]]; then
  echo "Error: tests/sandbox/ does not exist. Run tests/setup.sh first." >&2
  exit 1
fi

if [[ ! -f "$SANDBOX/package.json" ]]; then
  echo "Error: tests/sandbox/package.json not found. Run tests/setup.sh first." >&2
  exit 1
fi

if ! npm --prefix "$REPO_ROOT/tests" ls esbuild >/dev/null 2>&1 || \
   ! npm --prefix "$REPO_ROOT/tests" ls sass >/dev/null 2>&1; then
  echo "Error: esbuild or sass not installed. Run npm --prefix tests ci first." >&2
  exit 1
fi

# --- Start watchers ---

echo "Starting SCSS watcher..."

(
  cd "$SANDBOX"
  npm --prefix "$REPO_ROOT/tests" run --silent -- exec sass --watch \
    src/components/fpkit:src/components/fpkit \
    src/styles/theme:src/styles/theme \
    --no-source-map 2>&1
) &
SASS_PID=$!

# Trap to kill sass watcher on exit.
trap "kill '$SASS_PID' 2>/dev/null; wait '$SASS_PID' 2>/dev/null || true" EXIT INT TERM

# Give sass a moment to start watching.
sleep 1

# --- Auto-generate index.html ---

generate_index() {
  local index_file="$SANDBOX/index.html"
  local previews=()

  while IFS= read -r file; do
    previews+=("$file")
  done < <(find "$SANDBOX" -maxdepth 1 -name "*-preview.html" -type f | sort)

  if [[ ${#previews[@]} -eq 0 ]]; then
    return
  fi

  cat > "$index_file" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>acss-kit Sandbox — Preview Index</title>
  <style>
    body {
      font-family: system-ui, sans-serif;
      background: #f8f9fa;
      color: #1a1a1a;
      padding: 2rem;
      margin: 0;
    }
    h1 { font-size: 1.25rem; margin-bottom: 2rem; color: #444; font-weight: 500; }
    ul { list-style: none; padding: 0; margin: 0; }
    li { margin-bottom: 0.75rem; }
    a { color: #4f46e5; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .status {
      font-size: 0.875rem;
      color: #888;
      margin-top: 2rem;
      border-top: 1px solid #e5e7eb;
      padding-top: 1rem;
    }
  </style>
</head>
<body>
  <h1>acss-kit Sandbox — Component Previews</h1>
  <ul>
EOF

  for file in "${previews[@]}"; do
    local name=$(basename "$file" -preview.html)
    echo "    <li><a href=\"$(basename "$file")\">$name</a></li>" >> "$index_file"
  done

  cat >> "$index_file" <<'EOF'
  </ul>
  <div class="status">
    <p>Changes to <code>.scss</code>, <code>.css</code>, or <code>.html</code> files will auto-reload this page.</p>
    <p><strong>First-time rendering:</strong> If a preview renders unstyled on first load, save any <code>.scss</code> file to trigger compilation, then refresh the browser.</p>
  </div>
  <script>
    // Live-reload via esbuild's SSE endpoint.
    new EventSource('/esbuild').addEventListener('change', () => location.reload());
  </script>
</body>
</html>
EOF

  echo "Generated $index_file"
}

generate_index

# --- Find a free port ---

PORT=7743
MAX_PORT=7753
ESBUILD_PID=""

while [[ $PORT -le $MAX_PORT ]]; do
  npm --prefix "$REPO_ROOT/tests" run --silent -- exec esbuild --servedir="$SANDBOX" --serve="$PORT" >/dev/null 2>&1 &
  ESBUILD_PID=$!
  sleep 0.5
  if kill -0 "$ESBUILD_PID" 2>/dev/null; then
    break
  fi
  PORT=$((PORT + 1))
done

if [[ -z "$ESBUILD_PID" ]] || [[ $PORT -gt $MAX_PORT ]]; then
  echo "Error: Could not find a free port between 7743 and $MAX_PORT." >&2
  exit 1
fi

trap "kill '$ESBUILD_PID' 2>/dev/null; wait '$ESBUILD_PID' 2>/dev/null || true; kill '$SASS_PID' 2>/dev/null; wait '$SASS_PID' 2>/dev/null || true" EXIT INT TERM

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Serving http://localhost:$PORT/ (index: http://localhost:$PORT/index.html)"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "SCSS and HTML changes auto-reload. Press Ctrl+C to stop."
echo ""

wait "$ESBUILD_PID"
