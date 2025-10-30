# 🚂 Deploy Full System with Fuseki on Railway

## 🎯 Goal: Complete Working System

Deploy both Backend + Fuseki on Railway and connect them.

---

## 📋 Architecture

```
Railway Project: askPhysics
│
├─ Service 1: Backend (FastAPI)
│  └─ URL: https://askphysics-backend.up.railway.app
│
└─ Service 2: Fuseki (Knowledge Graph)
   └─ URL: https://askphysics-fuseki.up.railway.app
   └─ Internal: fuseki.railway.internal
```

---

## 🚀 Step-by-Step Deployment

### **Step 1: Push Fuseki Dockerfile to GitHub**

```bash
cd /Users/ronnie/Documents/askPhysics

# Add the new Dockerfile
git add Dockerfile.fuseki
git commit -m "Add Fuseki Dockerfile for Railway deployment"
git push origin main
```

---

### **Step 2: Deploy Fuseki Service on Railway**

1. **Go to Railway Dashboard**
   - Open [railway.app](https://railway.app)
   - Open your **askPhysics** project

2. **Add New Service**
   - Click **"+ New"** button (top right)
   - Select **"GitHub Repo"**
   - Choose your **askPhysics** repository
   - Railway creates a new service

3. **Configure Fuseki Service**

   **A. Click on the new service** (it might be building already)

   **B. Go to Settings:**
   - **Service Name:** `fuseki` (click service name to rename)

   **C. Set Dockerfile:**
   - **Root Directory:** Leave empty (root of repo)
   - **Dockerfile Path:** `Dockerfile.fuseki`
   - Railway should auto-detect this

   **D. Generate Domain:**
   - Settings → Networking
   - Click **"Generate Domain"**
   - You'll get something like: `https://askphysics-fuseki.up.railway.app`
   - **Copy this URL!**

4. **Wait for Deployment**
   - Click "Deployments" tab
   - Watch the build logs
   - Should take 3-5 minutes
   - Look for: "Fuseki ready!" in logs

---

### **Step 3: Connect Backend to Fuseki**

Now we need to tell your backend where Fuseki is.

#### **Option A: Use Public URL (Easier)**

1. **Go to Backend Service** in Railway
2. **Click "Variables" tab**
3. **Update or add:**
   ```
   FUSEKI_ENDPOINT=https://askphysics-fuseki.up.railway.app/plasma/query
   ```
   (Use the Fuseki URL you copied in Step 2)

4. **Backend will auto-redeploy** with new variable

#### **Option B: Use Private Network (Better)**

Railway services can talk to each other privately:

1. **Get Fuseki's private URL:**
   - Railway format: `fuseki.railway.internal:3030`
   - Or use the service reference variable

2. **Update backend environment:**
   ```
   FUSEKI_ENDPOINT=http://fuseki.railway.internal:3030/plasma/query
   ```

**Note:** Railway's internal networking requires services in same project.

---

### **Step 4: Verify Everything is Working**

#### **A. Check Fuseki**

```bash
# Replace with your actual Fuseki Railway URL
export FUSEKI_URL="https://askphysics-fuseki.up.railway.app"

# Test 1: Ping endpoint
curl $FUSEKI_URL/$/ping
# Expected: {"message":"ping"}

# Test 2: Query papers
curl -X POST $FUSEKI_URL/plasma/query \
  --data-urlencode "query=PREFIX : <http://example.org/plasma#> SELECT (COUNT(?p) as ?count) WHERE { ?p a :Paper }" \
  -H "Accept: application/sparql-results+json"

# Expected: JSON with paper count
```

#### **B. Check Backend Connection**

```bash
# Replace with your actual backend Railway URL
export BACKEND_URL="https://askphysics-backend.up.railway.app"

# Test 1: Health check (should show fuseki_connected: true)
curl $BACKEND_URL/health

# Test 2: Statistics (should return paper data)
curl $BACKEND_URL/statistics

# Test 3: Natural language query (FULL TEST!)
curl -X POST $BACKEND_URL/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "papers about tokamak", "limit": 5}' \
  | python3 -m json.tool
```

**If all tests pass:** 🎉 **Your full system is working!**

---

## 🐛 Troubleshooting

### **Issue 1: Fuseki Build Fails**

**Check:**
- Deployment logs in Railway
- Look for Java/Docker errors

**Common fixes:**
```bash
# Verify files exist locally
ls -la Dockerfile.fuseki
ls -la data/plasma_data.ttl
ls -la ontology/plasma_physics.ttl

# All should exist, then push again
git add .
git commit -m "Fix Fuseki deployment"
git push
```

---

### **Issue 2: Fuseki Starts but No Data**

**Symptoms:**
- Fuseki responds to `/$/ping`
- But queries return no results

**Check logs:**
1. Railway → Fuseki service → Logs
2. Look for "Loading data..." messages
3. Check for curl errors

**Fix:** Data might not be loading on startup. Try manual load:

```bash
# Get Railway CLI
npm i -g @railway/cli

# Login
railway login

# Connect to your project
railway link

# Run commands in Fuseki container
railway run curl -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary "@data/plasma_data.ttl" \
  http://localhost:3030/plasma/data
```

---

### **Issue 3: Backend Can't Connect to Fuseki**

**Symptoms:**
```
fuseki_connected: false
Connection refused
```

**Checks:**

1. **Verify Fuseki is running:**
   ```bash
   curl https://YOUR-FUSEKI-URL.up.railway.app/$/ping
   ```

2. **Verify FUSEKI_ENDPOINT variable:**
   - Backend service → Variables
   - Should be: `https://your-fuseki-url.up.railway.app/plasma/query`
   - NOT: `http://localhost:3030/...`

3. **Check for typos:**
   - URL should end with `/plasma/query`
   - Should be `https://` not `http://`

4. **Redeploy backend:**
   - Sometimes Railway needs a redeploy to pick up new variables
   - Backend service → Deployments → Click "Redeploy"

---

### **Issue 4: PORT Variable Issues**

Railway assigns port dynamically via `$PORT` variable.

**If Fuseki won't start, check:**

1. **Dockerfile uses PORT:**
   ```dockerfile
   CMD ./fuseki-server --port=${PORT:-3030}
   ```

2. **Railway sets PORT automatically:**
   - You don't need to set it manually
   - Railway assigns a random port

3. **Internal services use assigned port:**
   - Fuseki listens on Railway's assigned PORT
   - External URL routes to this port automatically

---

## 🔗 Railway Service Reference Variables

Railway provides automatic variables for service-to-service communication:

```bash
# In your backend, you can reference Fuseki like:
FUSEKI_ENDPOINT=${FUSEKI_URL}/plasma/query

# Where FUSEKI_URL is auto-generated by Railway
# pointing to your Fuseki service
```

**To use service references:**

1. **Backend Variables → Add:**
   ```
   FUSEKI_ENDPOINT=${{Fuseki.RAILWAY_PUBLIC_DOMAIN}}/plasma/query
   ```

2. **Railway auto-resolves** `Fuseki.RAILWAY_PUBLIC_DOMAIN` to your Fuseki URL

---

## ✅ Success Checklist

After deployment, verify:

### **Fuseki Service:**
- [ ] Deployment shows green checkmark ✅
- [ ] `/$/ping` responds with `{"message":"ping"}`
- [ ] Logs show "Fuseki ready!"
- [ ] Can query for paper count via SPARQL
- [ ] Has public domain generated

### **Backend Service:**
- [ ] Deployment shows green checkmark ✅
- [ ] `/health` shows `fuseki_connected: true`
- [ ] `/statistics` returns paper counts
- [ ] `/docs` shows API documentation
- [ ] Natural language query returns papers

### **Integration:**
- [ ] Backend can reach Fuseki
- [ ] Queries return actual data (not empty)
- [ ] No CORS errors
- [ ] Response times < 2 seconds

---

## 📊 Expected Results

After successful deployment:

### **Health Check Response:**
```json
{
  "status": "ok",
  "fuseki_connected": true,
  "version": "1.0.0"
}
```

### **Statistics Response:**
```json
{
  "papers": 100,
  "temperature": {
    "count": 24,
    "avg_kev": 6.5,
    "max_kev": 15.0,
    "min_kev": 0.003
  },
  "density": {
    "count": 4,
    "avg_density": 5.5e19,
    ...
  }
}
```

### **Natural Language Query Response:**
```json
{
  "parsed_query": {
    "intent": "search",
    "keywords": ["tokamak"],
    ...
  },
  "papers": [
    {
      "arxiv_id": "2510.24347v1",
      "title": "Physics-Informed Visual MARFE Prediction on the HL-3 Tokamak",
      ...
    }
  ],
  "total_results": 5
}
```

---

## 🎓 For Your Job Application

Once both services are deployed and connected:

### **Your Demo URLs:**

```
Frontend: https://askphysics-frontend.up.railway.app
Backend API: https://askphysics-backend.up.railway.app
Fuseki: https://askphysics-fuseki.up.railway.app
```

### **What to Say:**

> *"I've deployed a complete semantic search system with three components:*
>
> *1. **React Frontend** - Natural language search interface*
> *2. **FastAPI Backend** - Processes queries with GPT-4o and generates SPARQL*
> *3. **Apache Jena Fuseki** - RDF knowledge graph with 100+ papers*
>
> *Live demo at: https://askphysics.up.railway.app*
>
> *Try: 'Show me recent research on tokamak plasmas'*
>
> *The system demonstrates AI integration, semantic web technologies, and full-stack deployment skills."*

---

## 📈 Monitoring Your Deployment

**Railway Dashboard shows:**

```
┌─────────────────────────────────────┐
│ askPhysics Project                  │
├─────────────────────────────────────┤
│                                     │
│ 📦 Backend                          │
│ 🟢 Active                           │
│ Memory: 250MB / 512MB               │
│                                     │
│ 📦 Fuseki                           │
│ 🟢 Active                           │
│ Memory: 450MB / 1GB                 │
│                                     │
│ 📦 Frontend                         │
│ 🟢 Active                           │
│ Memory: 100MB / 512MB               │
└─────────────────────────────────────┘
```

**Usage:** Check "Usage" tab to monitor free tier credits

---

## 🎯 Quick Commands Reference

```bash
# Check Fuseki is alive
curl https://YOUR-FUSEKI-URL.up.railway.app/$/ping

# Count papers in knowledge graph
curl -X POST https://YOUR-FUSEKI-URL.up.railway.app/plasma/query \
  --data-urlencode "query=SELECT (COUNT(?p) as ?count) WHERE { ?p a <http://example.org/plasma#Paper> }" \
  -H "Accept: application/sparql-results+json"

# Test backend health
curl https://YOUR-BACKEND-URL.up.railway.app/health

# Full integration test
curl -X POST https://YOUR-BACKEND-URL.up.railway.app/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "papers about plasma", "limit": 3}' | jq .
```

---

## 🚀 You're Almost There!

Follow the steps above and you'll have:
- ✅ Backend deployed and running
- ✅ Fuseki deployed with your 100 papers
- ✅ Both services connected
- ✅ Natural language queries working end-to-end
- ✅ Professional demo ready for job application

**Estimated time:** 20-30 minutes

**Let's do this!** 🎉
