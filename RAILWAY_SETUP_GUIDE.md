# 🚂 Railway.app Backend Setup - Step-by-Step Guide

## 📋 Prerequisites

Before you start:
- [ ] Code pushed to GitHub
- [ ] Railway account created (sign up at railway.app with GitHub)

---

## 🎯 Part 1: Configure Backend on Railway

### Step 1: Create New Project

1. **Go to** [railway.app](https://railway.app)
2. **Click** "New Project" button (purple button, top right)
3. **Select** "Deploy from GitHub repo"
4. **Authorize Railway** to access your GitHub (if first time)
5. **Select your repository**: `askPhysics`

**What happens:** Railway will scan your repo and detect it's a Python project!

---

### Step 2: Railway Auto-Detection

Railway will automatically:
- ✅ Detect `requirements.txt` in `/backend` directory
- ✅ Identify it as a Python application
- ✅ Set up Python 3.12 environment
- ✅ Start building

**You'll see:** A deployment screen with build logs scrolling

---

### Step 3: Configure Backend Service

Once the initial deployment starts, configure it:

#### A. Set Root Directory

1. **Click** on your deployed service (shows as "askphysics" or similar)
2. **Click** "Settings" tab
3. **Scroll to** "Service Settings"
4. **Find** "Root Directory"
5. **Set to:** `backend`
6. **Click** "Update" or it auto-saves

**Why:** This tells Railway your backend code is in the `/backend` folder

---

#### B. Configure Build & Start Commands

Still in **Settings**:

1. **Find** "Build Command" section
2. **Set Build Command:**
   ```
   pip install -r requirements.txt
   ```

3. **Find** "Start Command" section
4. **Set Start Command:**
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **Save changes** (usually auto-saves)

**What this does:**
- **Build:** Installs all Python dependencies
- **Start:** Runs your FastAPI server on Railway's assigned port

---

#### C. Add Environment Variables

1. **Click** "Variables" tab (top of page)
2. **Click** "+ New Variable" button
3. **Add these variables:**

   **Variable 1:**
   ```
   Key: OPENAI_API_KEY
   Value: sk-your-actual-openai-key-here
   ```

   **Variable 2:**
   ```
   Key: FUSEKI_ENDPOINT
   Value: http://localhost:3030/plasma/query
   ```
   (We'll update this later if you deploy Fuseki separately)

   **Variable 3 (Optional):**
   ```
   Key: PORT
   Value: ${{PORT}}
   ```
   (Railway auto-sets this, but you can add it explicitly)

4. **Click** "Add" after each variable

**Important:** Railway will **automatically restart** your service when you add variables

---

### Step 4: Generate Public URL

1. **Go back to** "Settings" tab
2. **Scroll to** "Networking" section
3. **Click** "Generate Domain"

**Result:** Railway creates a public URL like:
```
https://askphysics-production.up.railway.app
```

**Copy this URL!** You'll need it for:
- Testing your backend
- Configuring your frontend
- Sharing in your job application

---

### Step 5: Monitor Deployment

1. **Click** "Deployments" tab
2. **Watch** the build logs
3. **Look for:**
   - ✅ "Building..."
   - ✅ "Installing dependencies..."
   - ✅ "Starting application..."
   - ✅ "Deployment successful"

**Typical build time:** 2-3 minutes

---

### Step 6: Test Your Backend

Once deployed (status shows green checkmark):

```bash
# Test 1: Health check
curl https://YOUR-RAILWAY-URL.up.railway.app/health

# Expected response:
# {"status":"ok","fuseki_connected":false,"version":"1.0.0"}

# Test 2: Statistics
curl https://YOUR-RAILWAY-URL.up.railway.app/statistics

# Test 3: Natural language query
curl -X POST https://YOUR-RAILWAY-URL.up.railway.app/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "papers about tokamak", "limit": 5}'
```

**If these work:** ✅ Your backend is live!

---

## 🎨 Part 2: Configure Frontend on Railway

### Step 1: Add Frontend Service

1. **In your Railway project**, click "+ New"
2. **Select** "GitHub Repo"
3. **Choose** your `askPhysics` repo again
4. **Railway will create a second service**

---

### Step 2: Configure Frontend Service

1. **Click** on the new service
2. **Go to** "Settings" tab

#### A. Set Root Directory
```
Root Directory: frontend
```

#### B. Set Build Command
```
Build Command: npm install && npm run build
```

#### C. Set Start Command
```
Start Command: npm run preview -- --host 0.0.0.0 --port $PORT
```

---

### Step 3: Add Frontend Environment Variables

1. **Click** "Variables" tab
2. **Add:**

   ```
   Key: VITE_API_URL
   Value: https://YOUR-BACKEND-RAILWAY-URL.up.railway.app
   ```

   (Use the backend URL from Part 1, Step 4)

---

### Step 4: Generate Frontend Domain

1. **Settings** → **Networking**
2. **Click** "Generate Domain"

**Result:** Frontend URL like:
```
https://askphysics-frontend.up.railway.app
```

---

## ✅ Verification Checklist

After both services are deployed:

### Backend Tests:
- [ ] `/health` endpoint returns 200
- [ ] `/statistics` returns paper count
- [ ] `/query/natural-language` accepts POST requests
- [ ] OpenAPI docs accessible at `/docs`

### Frontend Tests:
- [ ] Page loads without errors
- [ ] Can see the search interface
- [ ] Search box is functional
- [ ] Example query chips are clickable

### Integration Tests:
- [ ] Frontend can connect to backend
- [ ] Typing a query and clicking Search works
- [ ] Results display properly
- [ ] No CORS errors in browser console

---

## 🐛 Troubleshooting

### Issue: "Build Failed"

**Check:**
1. Go to "Deployments" tab → Click failed deployment
2. Read build logs for errors
3. Common issues:
   - Missing `requirements.txt`
   - Python version mismatch
   - Wrong root directory

**Fix:**
- Verify `Root Directory` is set to `backend`
- Check `requirements.txt` exists in `/backend` folder

---

### Issue: "Application Failed to Start"

**Check:**
1. Deployment logs for runtime errors
2. Common issues:
   - Import errors
   - Missing environment variables
   - Port binding issues

**Fix:**
- Verify start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Check all environment variables are set
- Look for error messages in logs

---

### Issue: "Cannot GET /"

**This is normal!** Your backend API doesn't have a root route.

**Test instead:**
- `/health` - Health check
- `/docs` - API documentation
- `/statistics` - Get data stats

---

### Issue: Frontend Can't Connect to Backend

**Check:**
1. CORS settings in `backend/main.py`
2. `VITE_API_URL` environment variable
3. Browser console for errors

**Fix:**
Ensure CORS allows Railway domains in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your Railway URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: "No OpenAI API Key" Warning

**This is OK!** The system will fall back to regex-only parsing.

**To enable LLM parsing:**
1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Add to Railway Variables: `OPENAI_API_KEY=sk-...`
3. Redeploy

---

### Issue: "Free Tier Credit Running Out"

**Monitor usage:**
1. Railway Dashboard → "Usage"
2. Free tier: $5/month

**Optimize:**
- Use smaller instance (Railway auto-configures)
- Remove unused services
- Or upgrade to Hobby plan ($5/month after free credit)

---

## 🎓 What Railway Auto-Detected

When you deployed, Railway automatically:

1. ✅ **Detected Python project** (found `requirements.txt`)
2. ✅ **Set Python 3.12** as runtime
3. ✅ **Installed dependencies** from `requirements.txt`
4. ✅ **Assigned a port** (via `$PORT` variable)
5. ✅ **Generated SSL certificate** (automatic HTTPS)
6. ✅ **Set up health checks**
7. ✅ **Enabled auto-deploy** (on git push)

---

## 🔄 Auto-Deploy Setup

**Great news:** Railway automatically redeploys on git push!

To enable:
1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update backend"
   git push
   ```
3. **Railway automatically detects the push and redeploys!**

**Watch deployment:**
- Railway Dashboard → "Deployments" tab
- You'll see new deployment starting automatically

---

## 📊 Railway Dashboard Overview

After setup, your Railway dashboard shows:

```
┌─────────────────────────────────────┐
│   askPhysics Project                │
├─────────────────────────────────────┤
│                                     │
│  📦 Backend Service                 │
│  🟢 Deployed                        │
│  URL: askphysics.up.railway.app    │
│                                     │
│  📦 Frontend Service                │
│  🟢 Deployed                        │
│  URL: askphysics-f.up.railway.app  │
│                                     │
└─────────────────────────────────────┘
```

---

## 🎯 Success Criteria

You'll know it's working when:

1. ✅ Backend URL opens API docs at `/docs`
2. ✅ Frontend URL loads the search interface
3. ✅ Typing a query and clicking "Search" returns results
4. ✅ No errors in browser console
5. ✅ No errors in Railway logs

---

## 💡 Pro Tips

1. **Custom Domain (Optional):**
   - Settings → Networking → "Custom Domain"
   - Add your own domain (e.g., `plasma-search.yourdomain.com`)

2. **View Logs:**
   - Click service → "Logs" tab
   - See real-time application logs
   - Great for debugging

3. **Restart Service:**
   - Settings → "Restart"
   - Useful after changing environment variables

4. **Clone Service:**
   - Useful for staging/production environments
   - Settings → "Clone Service"

---

## 📱 Share Your Demo

Once deployed, add to your application:

**In your resume:**
```
Plasma Physics Literature Search
Live Demo: https://askphysics.up.railway.app
```

**In your cover letter:**
```
I've deployed a working prototype at [URL] demonstrating:
- Natural language query processing (GPT-4o)
- Knowledge graph with 100+ papers
- Full-stack React + FastAPI + Fuseki implementation
```

**In your email:**
```
Subject: TIB FID Physik Application - [Your Name]

Dear Hiring Manager,

Please find my application attached. I've also created a live
demonstration of a plasma physics literature search system at:

https://askphysics.up.railway.app

Try queries like "recent papers about tokamak" to see the
AI-powered semantic search in action.

Best regards,
[Your Name]
```

---

## ✅ Final Checklist

Before sharing your deployed app:

- [ ] Backend `/health` returns OK
- [ ] Backend `/docs` shows API documentation
- [ ] Frontend loads without errors
- [ ] Can perform at least 3 different searches
- [ ] Results display correctly
- [ ] Tested on desktop browser
- [ ] Tested on mobile browser
- [ ] URLs saved for application
- [ ] Screenshots taken as backup

---

## 🎉 You're Live!

Your application is now:
- ✅ Deployed on professional infrastructure
- ✅ Accessible via public URL
- ✅ Auto-deploys on git push
- ✅ Running on HTTPS
- ✅ Ready to share in your job application

**Estimated total setup time:** 15-20 minutes

**Cost:** FREE (⁠$5/month credit covers ~500 hours)

---

## Need Help?

If you get stuck:
1. Check Railway logs (Deployments → Click deployment → View logs)
2. Review this guide's Troubleshooting section
3. Check Railway's documentation: [docs.railway.app](https://docs.railway.app)
4. Railway Discord community is very helpful

---

**Ready to deploy? Let's go! 🚀**
