#!/usr/bin/env bash
# Local dev server for previewing books.
# Usage: ./serve.sh [port]

PORT="${1:-8000}"
echo "Serving at http://localhost:$PORT"
echo "Books available at http://localhost:$PORT/books/"
python3 -m http.server "$PORT"
