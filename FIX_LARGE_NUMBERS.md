# Fix Large Numbers - Quick Guide

## Problem
Frontend showing: **Average: 92233720368547760.00 keV** ❌

This is **old/stale data** in Fuseki. The new TTL file is correct.

---

## Quick Fix (Recommended)

```bash
# 1. Stop Fuseki
docker-compose stop fuseki

# 2. Delete old database
rm -rf fuseki-data/databases/plasma/Data-0001/*

# 3. Start Fuseki
docker-compose up -d fuseki

# 4. Wait for startup
sleep 5

# 5. Upload new data (with admin password)
curl -u admin:admin123 -X POST http://localhost:3030/plasma/data \
  -H "Content-Type: text/turtle" \
  --data-binary @data/plasma_data.ttl

# 6. Restart backend
docker-compose restart backend

# 7. Test
curl http://localhost:8000/statistics
```

---

## Expected Result

```json
{
  "temperature": {
    "count": 30,
    "avg_kev": 1.08,    ← Should be ~1, not 92 quadrillion!
    "max_kev": 30.0,
    "min_kev": 0.0
  }
}
```

---

## If Upload Fails (401 Error)

Try with admin credentials:
```bash
curl -u admin:admin123 -X POST http://localhost:3030/plasma/data \
  -H "Content-Type: text/turtle" \
  --data-binary @data/plasma_data.ttl
```

Or use the Web UI:
1. Go to http://localhost:3030
2. Login: admin / admin123
3. Delete "plasma" dataset
4. Create new "plasma" dataset
5. Upload `data/plasma_data.ttl`

---

## Verify It Worked

```bash
# Check API
curl http://localhost:8000/statistics | jq '.temperature.avg_kev'
# Should return: 1.08

# Check Fuseki directly
curl -X POST http://localhost:3030/plasma/query \
  --data-urlencode "query=PREFIX : <http://example.org/plasma#> SELECT (MAX(?v) as ?max) WHERE { ?temp a :Temperature ; :normalizedValue ?v }" \
  -H "Accept: application/sparql-results+json"
# Should return max around 30.0
```

---

## What's Happening

- ✓ New TTL file has correct values (1-30 keV range)
- ✗ Fuseki has old sample data (with bad values)
- → Need to **clear Fuseki** and reload

