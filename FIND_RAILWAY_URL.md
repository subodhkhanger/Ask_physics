# 🔍 Where to Find Your Railway Project URL

## 📍 **Location of URL in Railway Dashboard**

### **After Deployment:**

Your URL is in **3 places** in Railway:

---

## **1️⃣ Main Dashboard (Easiest)**

```
┌──────────────────────────────────────────┐
│  Railway Dashboard                       │
├──────────────────────────────────────────┤
│                                          │
│  📦 askphysics (Backend Service)         │
│  ────────────────────────────────────    │
│  🟢 Active                               │
│                                          │
│  🌐 askphysics-production.up.railway.app│ ← YOUR URL HERE!
│     ↑ Click this to copy                │
│                                          │
└──────────────────────────────────────────┘
```

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Click on your **"askPhysics"** project
3. Look at your backend service card
4. **URL shows right on the card!** 🎉

---

## **2️⃣ Settings Tab (Networking Section)**

```
Steps:
1. Click your backend service
2. Click "Settings" tab (top menu)
3. Scroll to "Networking" section
4. You'll see:

   ┌─────────────────────────────────┐
   │ Networking                      │
   ├─────────────────────────────────┤
   │ Public Networking               │
   │                                 │
   │ Domains:                        │
   │ ✓ askphysics-production.up      │ ← YOUR URL
   │   .railway.app                  │
   │   [Copy URL]                    │
   │                                 │
   │ [+ Generate Domain]             │
   │ [+ Custom Domain]               │
   └─────────────────────────────────┘
```

**If you don't see a domain:**
- Click **"Generate Domain"** button
- Railway will create one automatically
- Format: `your-project-name.up.railway.app`

---

## **3️⃣ Deployments Tab**

```
Steps:
1. Click "Deployments" tab
2. Click on the latest deployment (green checkmark)
3. Look at top right:

   ┌─────────────────────────────────┐
   │ Deployment #123                 │
   │                                 │
   │ 🌐 askphysics-production.up     │ ← YOUR URL
   │    .railway.app                 │
   │    [Open]  [Copy]               │
   └─────────────────────────────────┘
```

---

## ✅ **How to Check if Project is Running**

### **Method 1: Visual Indicators in Railway**

Look for these status indicators:

```
🟢 Active / Running    ← Good! Project is live
🟡 Building           ← Wait, it's deploying
🔴 Failed             ← Error, check logs
⚪ Sleeping           ← Inactive (free tier limitation)
```

**Where to see status:**
- Main dashboard (on service card)
- Deployments tab (latest deployment status)

---

### **Method 2: Test URLs Directly**

Once you have your URL, test these endpoints:

#### **Test 1: Health Check**
```bash
curl https://YOUR-URL.up.railway.app/health
```

**Expected response:**
```json
{
  "status": "ok",
  "fuseki_connected": false,
  "version": "1.0.0"
}
```
✅ If you see this → **Backend is running!**

#### **Test 2: API Documentation**
Open in browser:
```
https://YOUR-URL.up.railway.app/docs
```
✅ If you see Swagger UI → **Backend is running!**

#### **Test 3: Statistics Endpoint**
```bash
curl https://YOUR-URL.up.railway.app/statistics
```
✅ If you get JSON response → **Backend is running!**

---

### **Method 3: View Logs**

```
Steps:
1. Click your backend service
2. Click "Logs" tab
3. Look for:
   ✓ "Application startup complete"
   ✓ "Uvicorn running on http://0.0.0.0:XXXX"
   ✓ No error messages
```

**Example good logs:**
```
INFO: Started server process [1]
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```
✅ If you see this → **Backend is running!**

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: "No Domain Generated"**

**Symptom:** No URL shown on dashboard

**Solution:**
```
1. Click service → Settings → Networking
2. Click "Generate Domain"
3. Wait 10 seconds
4. Copy the generated URL
```

---

### **Issue 2: "Service Sleeping" (⚪)**

**Symptom:** URL shows but service is asleep

**Why:** Free tier services sleep after inactivity

**Solution:**
```bash
# Wake it up by making a request
curl https://YOUR-URL.up.railway.app/health

# Wait 30 seconds for service to wake up
# Then service becomes active (🟢)
```

---

### **Issue 3: "Cannot GET /"**

**Symptom:** Opening URL shows "Cannot GET /"

**This is NORMAL!** Your backend has no root route.

**Test these instead:**
- `/health` - Health check
- `/docs` - API documentation
- `/statistics` - Data statistics

**Full URLs:**
```
https://YOUR-URL.up.railway.app/health
https://YOUR-URL.up.railway.app/docs
https://YOUR-URL.up.railway.app/statistics
```

---

### **Issue 4: "Application Error" or 500**

**Symptom:** URL returns error

**Check:**
1. **View Logs:**
   - Deployments tab → Latest deployment → View logs
   - Look for Python errors

2. **Check Environment Variables:**
   - Settings → Variables
   - Verify OPENAI_API_KEY is set

3. **Check Build Status:**
   - Deployments tab
   - Should show green checkmark ✅
   - If red ❌, click to see build logs

---

## 📱 **Quick Reference Card**

Save this for easy access:

```
┌─────────────────────────────────────────────┐
│ My Railway Project URLs                     │
├─────────────────────────────────────────────┤
│                                             │
│ Backend API:                                │
│ https://askphysics-production.up.railway.app│
│                                             │
│ Health Check:                               │
│ https://YOUR-URL.up.railway.app/health      │
│                                             │
│ API Docs:                                   │
│ https://YOUR-URL.up.railway.app/docs        │
│                                             │
│ Statistics:                                 │
│ https://YOUR-URL.up.railway.app/statistics  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🎯 **Step-by-Step: Finding Your URL Right Now**

### **If you've already deployed:**

1. **Open browser** → Go to [railway.app](https://railway.app)
2. **Login** with GitHub
3. **Click** "askPhysics" project (or whatever you named it)
4. **Look at the service card** → URL is displayed there
5. **Click the URL** to copy it
6. **Test it:**
   ```bash
   curl https://YOUR-COPIED-URL/health
   ```

### **If you haven't deployed yet:**

You won't have a URL until you:
1. Push code to GitHub
2. Deploy to Railway
3. Railway generates domain

**Then follow the steps above!**

---

## 🌐 **URL Format Explained**

Railway URLs follow this pattern:

```
https://[service-name]-[environment].up.railway.app

Examples:
https://askphysics-production.up.railway.app
https://backend-production-abc123.up.railway.app
https://my-app.up.railway.app
```

**Parts:**
- `service-name`: Your project/service name
- `environment`: Usually "production"
- `.up.railway.app`: Railway's domain

---

## ✅ **Verification Checklist**

To confirm everything is working:

- [ ] Can see URL in Railway dashboard
- [ ] URL opens (doesn't show error)
- [ ] `/health` endpoint returns 200 OK
- [ ] `/docs` shows Swagger UI
- [ ] Logs show "Application startup complete"
- [ ] Status indicator is 🟢 (green)
- [ ] No errors in logs

---

## 📸 **Visual Guide: Where to Look**

### **Dashboard View:**
```
My Projects
└─ askPhysics ←─ Click this
   ├─ Backend Service
   │  ├─ Status: 🟢 Active
   │  └─ URL: askphysics.up.railway.app ←─ HERE!
   └─ Frontend Service
      ├─ Status: 🟢 Active
      └─ URL: askphysics-f.up.railway.app ←─ HERE!
```

### **Settings View:**
```
Settings Tab
└─ Networking
   ├─ Public Networking
   │  └─ Domains:
   │     └─ askphysics.up.railway.app ←─ HERE!
   └─ [Generate Domain] ←─ Click if no URL
```

---

## 🎓 **For Your Job Application**

Once you have the URL, add it to your application:

**Resume:**
```
Plasma Physics Literature Search
Live Demo: https://askphysics.up.railway.app
GitHub: https://github.com/YOUR_USERNAME/askPhysics
```

**Cover Letter:**
```
I've deployed a working demonstration at:
https://askphysics.up.railway.app

The system demonstrates AI-powered semantic search
for plasma physics literature using GPT-4o and
knowledge graphs.
```

---

## 🆘 **Still Can't Find URL?**

**Option 1: Check Railway CLI**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# List projects
railway list

# Get service info (shows URL)
railway status
```

**Option 2: Contact Support**
- Railway has great support
- Check Railway Discord: discord.gg/railway
- Or docs: docs.railway.app

**Option 3: Redeploy**
- Sometimes URL isn't generated on first deploy
- Click "Redeploy" → New deployment should show URL

---

## 🎉 **Quick Test Command**

Once you have your URL:

```bash
# Replace YOUR-URL with actual URL
export BACKEND_URL="https://askphysics-production.up.railway.app"

# Test it
curl $BACKEND_URL/health && echo "✅ Backend is running!"
```

---

**Need help finding your specific URL?** Let me know and I can guide you through Railway's dashboard step-by-step! 🚀
