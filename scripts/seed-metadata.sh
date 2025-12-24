#!/bin/bash
# Seed all metadata (religions, castes, etc.)

set -e

echo "🌱 Seeding metadata..."
echo ""

# Run the seed script inside the backend container
docker compose exec backend python /app/init_seed/seed_all.py

echo ""
echo "✅ Metadata seeding complete!"
