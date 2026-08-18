# Deployment Guide for Railway.app

Railway is the easiest way to host Book Buzz online for free.

## What You Get

- ✅ **Free $5/month credit** (covers ~3-4 weeks of hosting)
- ✅ **Public URL** anyone can access (24/7 online)
- ✅ **Auto-deploys** from GitHub
- ✅ **Custom domain** option (optional)
- ✅ **Easy to manage** via web dashboard

---

## Step-by-Step Deployment

### 1. Create a GitHub Account (Free)

Go to https://github.com/join and sign up (takes 2 minutes)

### 2. Create a GitHub Repository

On GitHub:
- Click "+" → "New repository"
- Name: `BookClub` (or whatever you like)
- Description: `Book Buzz - Ranked Pairs Ballot Analysis`
- Choose "Public" or "Private"
- Click "Create repository"

### 3. Push Your Code to GitHub

On your computer, open a terminal/PowerShell and run:

```bash
# Navigate to your project
cd C:\Users\josep\PycharmProjects\BookClub

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial Book Buzz deployment"

# Add GitHub remote (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/BookClub.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**First time only:**
- GitHub will ask for authentication
- Use a Personal Access Token: https://github.com/settings/tokens
- Create token with `repo` scope
- Use token as password when prompted

### 4. Deploy to Railway

1. Go to https://railway.app
2. Click "Start New Project"
3. Choose "Deploy from GitHub"
4. Authorize GitHub (if needed)
5. Select your `BookClub` repository
6. Railway auto-detects Python and deploys!

### 5. Get Your Public URL

In the Railway dashboard:
- Go to "Deployments"
- Click on your app
- You'll see a URL like: `https://bookbuzz-production-xxxx.railway.app`
- This is your public link! Share it with anyone.

---

## Alternative: Quick Deploy with Railway CLI

If you prefer not to use GitHub:

```bash
# 1. Install Railway CLI: https://docs.railway.app/develop/cli

# 2. Login to Railway
railway login

# 3. Initialize and deploy
cd C:\Users\josep\PycharmProjects\BookClub
railway init
railway up
```

Railway will give you a URL instantly.

---

## Updating Your App

### If Using GitHub:
```bash
git add .
git commit -m "Updated features"
git push origin main
```
Railway auto-deploys within seconds!

### If Using Railway CLI:
```bash
railway up
```

---

## How Long Does It Last?

- **Free tier:** $5/month credit
- **Typical usage:** ~$1-2/month
- **Duration:** 2-5 months of free hosting
- **Auto-renews:** Free $5 credit each month (you just need a valid account)

After $5 is used, Railway will pause the app unless you add a payment method (but won't charge without permission).

---

## Monitoring & Management

In Railway dashboard:
- View **logs** (see errors, requests)
- Check **metrics** (CPU, memory, bandwidth)
- **Redeploy** older versions
- **Environment variables** (if needed later)

---

## If You Need Help

- Railway docs: https://docs.railway.app
- Railway support: support@railway.app
- GitHub docs: https://docs.github.com

---

## Making It Look Better (Optional)

### Get a Custom Domain
Railway lets you add a custom domain for free:
- Go to "Settings" → "Custom Domain"
- Use a free domain from freenom.com, or
- Use your own domain if you have one

### Example Domains
- bookbuzz.railway.app
- bookbuzz.mycompany.com

---

## Summary

1. Create GitHub account (free)
2. Create repository
3. Push code to GitHub
4. Connect Railway to GitHub
5. Get public URL
6. Share with anyone!

**Total setup time: ~10 minutes**

---

**Your app is now live! 🚀**

Share the URL with your book club and they can start analyzing ballots immediately!
