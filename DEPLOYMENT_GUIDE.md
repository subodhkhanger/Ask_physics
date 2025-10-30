# Deployment Guide - Free Hosting Options

## 🎯 Best Options for Job Application Demo

For a **job application portfolio**, here are the best FREE hosting options ranked by ease and impressiveness:

---

## ⭐ **Option 1: GitHub Pages + Render (RECOMMENDED)**

**Best for:** Quick demo, no cost, professional URL

### Architecture:
```
Frontend (React) → GitHub Pages (free, static)
Backend (FastAPI) → Render.com (free tier)
Fuseki (Knowledge Graph) → Render.com (free tier Docker)
```

### Pros:
- ✅ **100% Free**
- ✅ **Professional URLs** (yourusername.github.io)
- ✅ **Fast deployment** (5-10 minutes)
- ✅ **Easy to maintain**
- ✅ **Great for portfolios**

### Cons:
- ⚠️ Backend sleeps after 15 min inactivity (wakes up in ~30s)
- ⚠️ Fuseki data lost on restart (need to reload on startup)

---

## 🚀 **Option 2: Railway.app (EASIEST)**

**Best for:** All-in-one deployment, minimal config

### What is Railway?
- Modern hosting platform
- Free tier: $5/month credit (enough for demo)
- Deploys directly from GitHub
- Handles Docker, databases, everything

### Pros:
- ✅ **Easiest deployment** (connect GitHub, click deploy)
- ✅ **Handles everything** (frontend, backend, Fuseki)
- ✅ **Persistent data**
- ✅ **Custom domains**
- ✅ **No sleep mode** (within credit limits)

### Cons:
- ⚠️ Free tier limited to $5/month credit (~500 hours)
- ⚠️ After trial, need payment method (won't charge if under $5)

---

## 💻 **Option 3: Vercel + Railway (RECOMMENDED FOR SPEED)**

**Best for:** Fast frontend, reliable backend

### Architecture:
```
Frontend → Vercel (free, unlimited)
Backend + Fuseki → Railway (free $5 credit)
```

### Pros:
- ✅ **Blazing fast frontend** (Vercel CDN)
- ✅ **Professional setup**
- ✅ **Great free tiers**
- ✅ **Custom domains**
- ✅ **Perfect for React apps**

### Cons:
- ⚠️ Two platforms to manage
- ⚠️ Railway free tier limited

---

## 🆓 **Option 4: AWS Free Tier (Most Professional)**

**Best for:** Showing enterprise skills, long-term hosting

### Services Used (All Free Tier):
- **EC2** (t2.micro): Backend + Fuseki
- **S3 + CloudFront**: Frontend static hosting
- **RDS** (optional): Database if needed

### Pros:
- ✅ **Most professional** (shows AWS knowledge)
- ✅ **12 months free**
- ✅ **Resume-worthy**
- ✅ **No sleep mode**
- ✅ **Persistent data**

### Cons:
- ⚠️ **More complex setup** (2-3 hours)
- ⚠️ **Requires credit card**
- ⚠️ **Can incur charges** if misconfigured
- ⚠️ **Maintenance overhead**

---

## 📝 **Detailed Deployment Instructions**

---

## 🌟 OPTION 1: GitHub Pages + Render (Recommended)

### Step 1: Deploy Frontend to GitHub Pages

```bash
cd /Users/ronnie/Documents/askPhysics/frontend

# Build production version
npm run build

# The build creates a 'dist' folder
```

#### Create GitHub Repo and Deploy:

```bash
# In your project root
cd /Users/ronnie/Documents/askPhysics

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit - Plasma Physics Search"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/askPhysics.git
git branch -M main
git push -u origin main

# Deploy frontend to GitHub Pages
cd frontend
npm install -g gh-pages  # One-time install

# Add to package.json:
# "homepage": "https://YOUR_USERNAME.github.io/askPhysics",
# "predeploy": "npm run build",
# "deploy": "gh-pages -d dist"

# Deploy
npm run deploy
```

**Result:** Frontend live at `https://YOUR_USERNAME.github.io/askPhysics`

---

### Step 2: Deploy Backend to Render

1. **Go to [render.com](https://render.com)** and sign up (free)

2. **Click "New +"** → **"Web Service"**

3. **Connect your GitHub repo**

4. **Configure:**
   - Name: `askphysics-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

5. **Add Environment Variables:**
   - `OPENAI_API_KEY`: (your key)
   - `FUSEKI_ENDPOINT`: (we'll add this after Fuseki is deployed)

6. **Click "Create Web Service"**

**Result:** Backend API at `https://askphysics-api.onrender.com`

---

### Step 3: Deploy Fuseki to Render

1. **Create `Dockerfile` for Fuseki:**

```dockerfile
# /Users/ronnie/Documents/askPhysics/fuseki.Dockerfile
FROM openjdk:11-jre-slim

# Install Fuseki
RUN apt-get update && apt-get install -y wget && \
    wget https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.10.0.tar.gz && \
    tar -xzf apache-jena-fuseki-4.10.0.tar.gz && \
    mv apache-jena-fuseki-4.10.0 /fuseki && \
    rm apache-jena-fuseki-4.10.0.tar.gz

WORKDIR /fuseki

# Copy data files
COPY data/plasma_data.ttl /fuseki/data/
COPY ontology/plasma_physics.ttl /fuseki/ontology/

# Expose port
EXPOSE 3030

# Start Fuseki with data loaded
CMD ["./fuseki-server", "--update", "--mem", "/plasma"]
```

2. **On Render:**
   - Click "New +" → **"Web Service"**
   - Connect GitHub repo
   - Name: `askphysics-fuseki`
   - Environment: `Docker`
   - Dockerfile Path: `fuseki.Dockerfile`
   - Plan: **Free**

3. **Note the URL:** `https://askphysics-fuseki.onrender.com`

4. **Update backend environment variable:**
   - Go to backend service settings
   - Set `FUSEKI_ENDPOINT`: `https://askphysics-fuseki.onrender.com/plasma/query`

**Result:** Complete system online!

---

## 🚂 OPTION 2: Railway.app (Easiest)

### Step 1: Sign Up

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (free $5 credit)

### Step 2: Deploy Backend

1. **Click "New Project"** → **"Deploy from GitHub repo"**
2. Select your `askPhysics` repo
3. **Add Service** → **"Backend"**
4. Configure:
   ```
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. **Add Variables:**
   - `OPENAI_API_KEY`: your key

### Step 3: Deploy Fuseki

1. **Add Service** → **"Fuseki"**
2. **Dockerfile:**
   - Use the same Dockerfile from Option 1
3. Railway will auto-detect and deploy

### Step 4: Deploy Frontend

1. **Add Service** → **"Frontend"**
2. Configure:
   ```
   Root Directory: frontend
   Build Command: npm run build
   Start Command: npm run preview
   ```
3. **Add Variable:**
   - `VITE_API_URL`: (your backend Railway URL)

**Result:** All services live with persistent URLs!

**URLs will be like:**
- Frontend: `https://askphysics.up.railway.app`
- Backend: `https://askphysics-backend.up.railway.app`
- Fuseki: `https://askphysics-fuseki.up.railway.app`

---

## ☁️ OPTION 3: Vercel + Railway

### Frontend on Vercel:

1. **Go to [vercel.com](https://vercel.com)**
2. **Import Git Repository**
3. **Configure:**
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Environment Variables:**
   - `VITE_API_URL`: (your Railway backend URL)
5. **Deploy**

**Result:** Frontend at `https://askphysics.vercel.app` (super fast!)

### Backend on Railway:
- Follow Railway steps from Option 2

---

## 🏢 OPTION 4: AWS Free Tier

### Prerequisites:
- AWS account
- Credit card (required but won't be charged in free tier)
- Basic AWS knowledge

### Architecture:
```
Route 53 (optional) → CloudFront → S3 (frontend)
                    → ALB → EC2 (backend + Fuseki)
```

### Step 1: Deploy Frontend to S3 + CloudFront

```bash
# Build frontend
cd frontend
npm run build

# Install AWS CLI
brew install awscli

# Configure AWS
aws configure

# Create S3 bucket
aws s3 mb s3://askphysics-frontend

# Upload build files
aws s3 sync dist/ s3://askphysics-frontend --acl public-read

# Enable static website hosting
aws s3 website s3://askphysics-frontend --index-document index.html
```

### Step 2: Launch EC2 Instance

1. **AWS Console** → **EC2** → **Launch Instance**
2. **Select:** Ubuntu Server 22.04 (free tier eligible)
3. **Instance Type:** t2.micro (free tier)
4. **Storage:** 8 GB (free tier)
5. **Security Group:** Open ports 22, 80, 443, 3030, 8000

### Step 3: Setup EC2

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install -y python3-pip docker.io git

# Clone your repo
git clone https://github.com/YOUR_USERNAME/askPhysics.git
cd askPhysics

# Start Fuseki with Docker
sudo docker compose up -d

# Start Backend
cd backend
pip3 install -r requirements.txt
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### Step 4: Configure Frontend

Update `frontend/.env.production`:
```
VITE_API_URL=http://your-ec2-ip:8000
```

Rebuild and redeploy to S3.

**Result:** Professional AWS-hosted application!

---

## 📊 Comparison Table

| Feature | GitHub + Render | Railway | Vercel + Railway | AWS Free Tier |
|---------|----------------|---------|------------------|---------------|
| **Cost** | Free | Free ($5 credit) | Free | Free (12 months) |
| **Setup Time** | 15 min | 5 min | 10 min | 2-3 hours |
| **Difficulty** | Easy | Easiest | Easy | Hard |
| **Sleep Mode** | Yes | No | Frontend: No, Backend: No | No |
| **Custom Domain** | Limited | Yes | Yes | Yes |
| **Data Persistence** | No | Yes | Yes | Yes |
| **Resume Value** | Good | Good | Great | Excellent |
| **Best For** | Quick demo | Easiest deploy | Fast frontend | Enterprise demo |

---

## 🎯 My Recommendation for Job Application

### For TIB FID Physik Application:

**Use: Railway.app (Option 2)**

**Why:**
1. ✅ **Fastest deployment** (5-10 minutes)
2. ✅ **No sleep mode** (important for demo)
3. ✅ **Professional URLs**
4. ✅ **Actually works** (no restart issues)
5. ✅ **Shows you can deploy full-stack apps**

### Alternative if Railway credit runs out:

**Use: Vercel + Render (Hybrid)**
- Frontend on Vercel (always fast, never sleeps)
- Backend on Render (tolerates 30s wake-up time)

---

## 🚀 Quick Start: Railway Deployment

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to railway.app
# 3. Click "New Project" → "Deploy from GitHub"
# 4. Select askPhysics repo
# 5. Railway auto-detects and deploys!

# 6. Add environment variables in Railway dashboard:
#    - OPENAI_API_KEY
#    - FUSEKI_ENDPOINT (auto-set by Railway)

# Done! Your app is live!
```

**Result:** Working demo at a professional URL in under 10 minutes!

---

## 📝 Post-Deployment Checklist

- [ ] Frontend loads correctly
- [ ] Backend API responds (`/health` endpoint)
- [ ] Fuseki has data (check `/statistics` endpoint)
- [ ] Natural language query works
- [ ] Test at least 3 example queries
- [ ] Add URL to your resume/application
- [ ] Test on mobile device

---

## 🎓 For Your Application

Include this in your cover letter:

> *"I've deployed a live demo at [YOUR_URL]. The system uses React (frontend), FastAPI (backend), Apache Jena Fuseki (knowledge graph), and GPT-4o for natural language processing. Feel free to try queries like 'recent papers about tokamak' to see the AI-powered semantic search in action."*

---

## 🆘 Troubleshooting Deployment

### Render "Build Failed"
- Check `requirements.txt` includes all dependencies
- Verify Python version compatibility
- Check build logs in Render dashboard

### Railway "Out of Credit"
- Free tier: $5/month (~500 hours)
- Optimize: Use smaller Docker images
- Alternative: Switch to Render for backend

### CORS Errors
Add to `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Can't Connect to Backend
- Check `VITE_API_URL` environment variable
- Verify backend URL is correct (https, not http if on Render/Railway)
- Check browser console for CORS errors

---

## 💡 Pro Tips

1. **Use Railway for demo day** - No sleep mode means instant demos
2. **Add custom domain** - Makes it more professional
3. **Monitor logs** - Catch errors before your interview
4. **Test on mobile** - Interviewers might check on phones
5. **Have backup** - Keep local demo ready just in case

---

## 🎉 You're Ready to Deploy!

**Recommended path for your situation:**

1. **Quick demo (1 week out):** Railway.app
2. **Permanent portfolio:** AWS Free Tier
3. **Budget-conscious:** GitHub Pages + Render

**Start with Railway - you can always migrate later!**

Would you like me to help you deploy to Railway right now?
