# 🚀 Deploy Your App in 10 Minutes - Railway

## Why Railway?
- ✅ **Easiest** of all options
- ✅ **Free $5/month credit** (enough for demos)
- ✅ **No sleep mode** (instant response for interviewers)
- ✅ **Deploys from GitHub automatically**
- ✅ **Perfect for job applications**

---

## Step-by-Step Deployment

### 1️⃣ Push to GitHub (If not already done)

```bash
cd /Users/ronnie/Documents/askPhysics

# Initialize git
git init
git add .
git commit -m "Plasma Physics Literature Search - Ready for deployment"

# Create repo on GitHub.com:
# - Go to github.com
# - Click "+" → "New repository"
# - Name: "askPhysics"
# - Click "Create repository"

# Then push:
git remote add origin https://github.com/YOUR_USERNAME/askPhysics.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ Deploy to Railway

#### A. Sign Up
1. Go to **[railway.app](https://railway.app)**
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway

#### B. Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **"askPhysics"** repository

#### C. Configure Backend
Railway will auto-detect it's a Python app!

1. Click on the **backend service**
2. Go to **Settings** → **Environment**
3. Add variables:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
4. Go to **Settings** → **Networking**
5. Click **"Generate Domain"**
6. **Copy the URL** (like: `askphysics-backend.up.railway.app`)

#### D. Configure Frontend
1. Click **"+ New"** → **"GitHub Repo"** → Select `askPhysics` again
2. In **Settings** → **Root Directory**: `frontend`
3. In **Settings** → **Build Command**: `npm run build`
4. In **Settings** → **Start Command**: `npm run preview`
5. Go to **Variables** → Add:
   ```
   VITE_API_URL=https://YOUR-BACKEND-URL.up.railway.app
   ```
   (Use the backend URL from step C.6)
6. Go to **Settings** → **Networking** → **Generate Domain**
7. **Copy the frontend URL**

#### E. Deploy Fuseki (Optional - Can use in-memory)
1. Click **"+ New"** → **"Empty Service"**
2. Use Docker deployment
3. Or skip this and let backend use an external Fuseki

---

### 3️⃣ Test Your Deployment

```bash
# Test backend health
curl https://YOUR-BACKEND-URL.up.railway.app/health

# Test natural language query
curl -X POST https://YOUR-BACKEND-URL.up.railway.app/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "papers about tokamak", "limit": 5}'
```

**Open frontend:** `https://YOUR-FRONTEND-URL.up.railway.app`

---

## 🎯 Even Simpler: Vercel (Frontend Only)

If you just want to deploy the frontend quickly:

```bash
# Install Vercel CLI
npm install -g vercel

# Go to frontend directory
cd frontend

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (Your account)
# - Link to existing project? No
# - What's your project's name? askphysics
# - In which directory is your code located? ./
# - Want to override the settings? No

# Done! You'll get a URL like: https://askphysics.vercel.app
```

---

## 📋 Quick Comparison

| Platform | Setup Time | Free Tier | Best For |
|----------|-----------|-----------|----------|
| **Railway** | 10 min | $5/month credit | Full app (backend + frontend) |
| **Vercel** | 2 min | Unlimited | Frontend only (blazing fast) |
| **Render** | 15 min | Limited hours | Backend (free but sleeps) |
| **Netlify** | 2 min | Unlimited | Frontend only |

---

## 🏆 Recommended Setup for Job Application

### Best: Railway (All-in-One)
- Frontend, backend, everything in one place
- One URL to share: `https://askphysics.up.railway.app`
- Professional and reliable

### Alternative: Vercel + Render
- Frontend on Vercel (super fast): `https://askphysics.vercel.app`
- Backend on Render (free but sleeps): `https://askphysics-api.onrender.com`
- Combined best of both

---

## 💡 Pro Tips for Demo Day

1. **Test before interview**: Open the URL 5 minutes before your interview to wake up services
2. **Use custom domain** (optional): Railway/Vercel allow free custom domains
3. **Add to resume**: Include the live demo URL
4. **Screenshot results**: Have backup images in case of network issues
5. **Mention in cover letter**: "Live demo available at [URL]"

---

## 🆘 Common Issues

### "Cannot connect to backend"
- Check `VITE_API_URL` in frontend environment variables
- Make sure it starts with `https://` (not `http://`)
- Verify backend is deployed and running

### "Build failed" on Railway
- Check that `requirements.txt` is in `backend/` directory
- Verify Python version compatibility
- Check build logs in Railway dashboard

### "No data returned" from queries
- Backend needs to load Fuseki data on startup
- May need to modify backend to include embedded data
- Or redeploy Fuseki service separately

---

## ✅ Deployment Checklist

Before sharing your demo URL:

- [ ] Frontend loads without errors
- [ ] Backend `/health` endpoint responds
- [ ] Can see statistics (paper count, etc.)
- [ ] Natural language search returns results
- [ ] Tested at least 3 different queries
- [ ] Works on mobile browser
- [ ] URL added to resume/application
- [ ] Sent test email to yourself with URL

---

## 🎓 What to Say in Your Application

> *"I've deployed a live demonstration of the system at [YOUR_URL]. The application features:*
>
> *- **Natural language search** powered by GPT-4o*
> *- **Knowledge graph** with 100+ plasma physics papers from arXiv*
> *- **SPARQL queries** dynamically generated from user intent*
> *- **Full-stack implementation**: React frontend, FastAPI backend, Apache Jena Fuseki*
>
> *Try queries like 'recent papers about tokamak' or 'research on plasma acceleration' to see the AI-powered semantic search in action."*

---

## 🚀 Ready to Deploy?

**Fastest path:**

1. Push to GitHub (5 min)
2. Deploy to Railway (5 min)
3. Test and share URL

**Total time: 10 minutes from now to live demo!**

Would you like help with any of these steps?
