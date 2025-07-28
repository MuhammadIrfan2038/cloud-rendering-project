#!/usr/bin/env bash
# wait-for-it.sh

host="$1"
port="$2"
shift 2
cmd="$@"

echo "⏳ Waiting for $host:$port to be ready..."
until nc -z "$host" "$port"; do sleep 1
done

echo "✅ $host:$port is up! Running command: $cmd"
exec $cmd
