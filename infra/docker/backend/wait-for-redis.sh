#!/bin/bash
# Wait for Redis to be ready before starting the application

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "⏳ Waiting for Redis at $host:$port..."

# Wait for Redis to respond to ping
until redis-cli -h "$host" -p "$port" ping > /dev/null 2>&1; do
  echo "⏳ Redis is unavailable - sleeping"
  sleep 1
done

echo "✅ Redis is up - executing command"
exec $cmd