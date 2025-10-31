# Firebase Analytics Setup Guide

This guide will help you set up Firebase Analytics for the Plasma Physics Literature Search application.

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or select an existing project
3. Enter project name (e.g., "Plasma Physics Search")
4. (Optional) Enable Google Analytics
5. Click **"Create project"**

## Step 2: Register Web App

1. In your Firebase project, click the **Web icon** (</>) to add a web app
2. Enter app nickname (e.g., "Plasma Search Frontend")
3. Check **"Also set up Firebase Hosting"** (optional)
4. Click **"Register app"**
5. **Copy the Firebase configuration object** - you'll need these values

The config will look like this:
```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef",
  measurementId: "G-XXXXXXXXXX"
};
```

## Step 3: Configure Environment Variables

### For Local Development

Create a `.env` file in the `frontend/` directory:

```bash
cd frontend
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
EOF
```

### For Railway Production

Add these environment variables in Railway Dashboard:

1. Go to your Frontend service in Railway
2. Click **Variables** tab
3. Add each variable:

| Variable Name | Example Value |
|--------------|---------------|
| `VITE_API_URL` | `https://askphysics-production.up.railway.app` |
| `VITE_FIREBASE_API_KEY` | `AIza...` |
| `VITE_FIREBASE_AUTH_DOMAIN` | `your-project.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | `your-project-id` |
| `VITE_FIREBASE_STORAGE_BUCKET` | `your-project.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | `123456789` |
| `VITE_FIREBASE_APP_ID` | `1:123:web:abc` |
| `VITE_FIREBASE_MEASUREMENT_ID` | `G-XXXXXXXXXX` |

4. Click **"Redeploy"** to rebuild with the new variables

## Step 4: Enable Analytics in Firebase

1. In Firebase Console, go to **Analytics** → **Dashboard**
2. Wait a few minutes for data to start flowing
3. You should see events appearing in real-time

## Step 5: Verify Analytics is Working

### Check Browser Console

Open your app in a browser and check the console:
- You should see: `"Firebase Analytics initialized"`
- If not configured: `"Firebase Analytics disabled (no config found)"`

### Check Firebase Console

1. Go to Firebase Console → **Analytics** → **Events**
2. Click on **"View real-time data"**
3. Navigate around your app - you should see events appearing:
   - `page_view` - When users visit pages
   - `natural_language_query` - When users search
   - `view_paper` - When users click on papers
   - `api_call` - API interactions

## Analytics Events Tracked

The app automatically tracks these events:

| Event Name | Description | Parameters |
|------------|-------------|------------|
| `page_view` | Page navigation | `page_name` |
| `natural_language_query` | NL query submitted | `query`, `result_count` |
| `view_paper` | Paper viewed | `paper_id` |
| `search_papers` | Search performed | `search_query` |
| `filter_temperature` | Temperature filter applied | `min_temp`, `max_temp` |
| `filter_density` | Density filter applied | `min_density`, `max_density` |
| `api_call` | API request made | `endpoint`, `success`, `duration_ms` |

## Optional: Add More Analytics

To track additional events in your components:

```typescript
import { analyticsEvents } from '../lib/firebase';

// Track a paper view
analyticsEvents.viewPaper(paperId);

// Track a search
analyticsEvents.searchPapers(searchQuery);

// Track a natural language query
analyticsEvents.naturalLanguageQuery(query, results.length);
```

## Troubleshooting

### Analytics Not Showing Data

1. **Check environment variables are set** - Look in Railway Variables tab
2. **Rebuild the app** - Vite bakes env vars at build time
3. **Wait 24 hours** - Some reports take time to populate
4. **Check browser console** - Look for Firebase initialization message
5. **Verify measurementId** - Must start with `G-`

### CORS Errors

If you see CORS errors, add your domain to Firebase:

1. Go to Firebase Console → **Authentication** → **Settings**
2. Scroll to **Authorized domains**
3. Add your Railway domain: `frontend-production-585a.up.railway.app`

### Ad Blockers

Some ad blockers block Firebase Analytics. Test in incognito mode or disable ad blockers.

## Privacy Considerations

Firebase Analytics is GDPR compliant when configured properly. Consider:

1. Adding a **Cookie Consent Banner** for EU users
2. Updating your **Privacy Policy** to mention analytics
3. Allowing users to **opt-out** of tracking

Example opt-out code:
```typescript
// Disable analytics
import { setAnalyticsCollectionEnabled } from 'firebase/analytics';
setAnalyticsCollectionEnabled(analytics, false);
```

## Cost

Firebase Analytics is **completely free** with no limits on events or users.

## Next Steps

1. Set up **Custom Audiences** for remarketing
2. Configure **Conversion Events** for goal tracking
3. Link to **Google Ads** for campaign tracking
4. Export data to **BigQuery** for advanced analysis

## Support

- [Firebase Documentation](https://firebase.google.com/docs/analytics)
- [Analytics Event Reference](https://firebase.google.com/docs/reference/js/analytics)
- [Best Practices](https://firebase.google.com/docs/analytics/best-practices)
