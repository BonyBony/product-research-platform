# YouTube API Setup Guide

Get your YouTube Data API v3 key in 5 minutes!

## Step-by-Step Instructions

### 1. Go to Google Cloud Console

Visit: **https://console.cloud.google.com/**

- Sign in with your Google account
- If you don't have one, create a free Google account first

### 2. Create a New Project

1. Click on the **project dropdown** at the top (next to "Google Cloud")
2. Click **"NEW PROJECT"** in the top right
3. Enter project name: `ResearchAI` (or any name you like)
4. Click **"CREATE"**
5. Wait a few seconds for the project to be created
6. Make sure the new project is selected (check the dropdown at top)

### 3. Enable YouTube Data API v3

1. In the search bar at the top, type: **"YouTube Data API v3"**
2. Click on **"YouTube Data API v3"** in the results
3. Click the blue **"ENABLE"** button
4. Wait a few seconds for it to enable

### 4. Create API Credentials

1. After enabling, you'll see a page with a **"CREATE CREDENTIALS"** button
2. Click **"CREATE CREDENTIALS"**
3. In the dropdown, select **"API key"**
4. A popup will show your API key that looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
5. **COPY THIS KEY** - you'll need it in a moment
6. Click **"CLOSE"** (or **"RESTRICT KEY"** if you want to add restrictions)

### 5. (Optional but Recommended) Restrict Your API Key

For security, restrict your key to only YouTube API:

1. After creating the key, click on the key name to edit it
2. Under **"API restrictions"**, select **"Restrict key"**
3. In the dropdown, find and check **"YouTube Data API v3"**
4. Click **"SAVE"**

### 6. You're Done!

Your API key is ready to use immediately.

**Your key looks like:**
```
AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## Quick Navigation Links

Once you're logged into Google Cloud Console:

1. **API Dashboard**: https://console.cloud.google.com/apis/dashboard
2. **Enable APIs**: https://console.cloud.google.com/apis/library
3. **Credentials**: https://console.cloud.google.com/apis/credentials
4. **YouTube Data API v3**: https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com

---

## Free Tier Limits

YouTube Data API v3 Free Tier:
- ✅ **10,000 quota units per day** (FREE)
- ✅ Each search costs ~100 units
- ✅ Each comment thread costs ~1 unit
- ✅ **You can make ~50-100 research queries per day for FREE**

This is more than enough for your MVP!

---

## Troubleshooting

### "API not enabled" error
- Go back to step 3 and make sure you clicked "ENABLE"
- Wait a few minutes for it to fully enable

### "Quota exceeded" error
- You've hit the daily limit (10,000 units)
- Wait until tomorrow (resets at midnight Pacific Time)
- Or request a quota increase (usually approved automatically)

### "Invalid API key" error
- Make sure you copied the entire key
- No extra spaces before/after the key
- Key should start with `AIza`

### Can't find the project
- Make sure you're selecting the right project from the dropdown at the top
- The project name is shown next to "Google Cloud" logo

---

## Quota Management

Each API call costs "quota units":

| Operation | Cost |
|-----------|------|
| Search videos | ~100 units |
| Get video details | ~1 unit |
| Get comment threads | ~1 unit per thread |

**For one ResearchAI query:**
- 1 search (~100 units)
- Get 10 video details (~10 units)
- Get 50 comment threads (~50 units)
- **Total: ~160 units per research query**

**Daily limit: 10,000 units = ~60 research queries per day**

---

## What's Next?

Once you have your API key:

1. Copy the API key
2. Provide it to me
3. I'll update your `.env` file
4. Build the YouTube integration
5. Test with real data!

---

## Cost Information

**YouTube Data API v3 is FREE** up to 10,000 quota units/day.

If you need more:
- Request a quota increase in Google Cloud Console
- Most increases are approved automatically for reasonable limits
- Still FREE, just higher limits

**No credit card required for the free tier!**

---

## Security Best Practices

1. ✅ Restrict your API key to YouTube Data API v3 only
2. ✅ Never commit your API key to Git (already in .gitignore)
3. ✅ Rotate your key every few months
4. ✅ If compromised, delete the old key and create a new one

---

## Ready?

Once you have your YouTube API key (starts with `AIza`), provide it and I'll:

1. Update your `.env` file
2. Build the YouTube service
3. Update the research endpoint
4. Test with real YouTube comments
5. Show you the results!

Let's do this! 🚀
