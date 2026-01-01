#!/bin/bash
set -e

echo "🗄️  Setting up wakanda_DB databases..."

# Start Docker Compose services
docker-compose up -d

# Wait for PostgreSQL main to be healthy
echo "⏳ Waiting for PostgreSQL (main) to be ready..."
until docker exec wakanda-postgres-main pg_isready -U national_Unity -d wakanda_DB; do
  sleep 2
done

# Wait for PostgreSQL replica to be healthy
echo "⏳ Waiting for PostgreSQL (replica) to be ready..."
until docker exec wakanda-postgres-replica pg_isready -U national_Unity -d wakanda_DB; do
  sleep 2
done

# Wait for CockroachDB nodes to be healthy
echo "⏳ Waiting for CockroachDB (node1) to be ready..."
until curl -f http://localhost:8080/health?ready=1 > /dev/null 2>&1; do
  sleep 2
done

echo "⏳ Waiting for CockroachDB (node2) to be ready..."
until curl -f http://localhost:8081/health?ready=1 > /dev/null 2>&1; do
  sleep 2
done

echo "⏳ Waiting for CockroachDB (node3) to be ready..."
until curl -f http://localhost:8082/health?ready=1 > /dev/null 2>&1; do
  sleep 2
done

# Initialize CockroachDB cluster (idempotent)
echo "🔧 Initializing CockroachDB cluster..."
docker exec wakanda-cockroachdb-1 ./cockroach init --insecure --host=cockroachdb-1:26257 || true

# Create wakanda_DB in CockroachDB with national_Unity user
echo "🔧 Creating wakanda_DB in CockroachDB..."
docker exec wakanda-cockroachdb-1 ./cockroach sql --insecure --execute="CREATE DATABASE IF NOT EXISTS wakanda_DB;"
docker exec wakanda-cockroachdb-1 ./cockroach sql --insecure --execute="CREATE USER IF NOT EXISTS national_Unity;"
docker exec wakanda-cockroachdb-1 ./cockroach sql --insecure --execute="GRANT ALL ON DATABASE wakanda_DB TO national_Unity;"

echo "✅ All databases ready!"
echo ""
echo "📍 Connection strings:"
echo "   PostgreSQL (main):    postgres://national_Unity:northeastMv@10111@localhost:5432/wakanda_DB"
echo "   PostgreSQL (replica): postgres://national_Unity:northeastMv@10111@localhost:5433/wakanda_DB"
echo "   CockroachDB (n1):     postgres://national_Unity@localhost:26257/wakanda_DB?sslmode=disable"
echo "   CockroachDB (n2):     postgres://national_Unity@localhost:26258/wakanda_DB?sslmode=disable"
echo "   CockroachDB (n3):     postgres://national_Unity@localhost:26259/wakanda_DB?sslmode=disable"
echo ""
echo "🎯 CockroachDB UI: http://localhost:8080 (n1), http://localhost:8081 (n2), http://localhost:8082 (n3)"
