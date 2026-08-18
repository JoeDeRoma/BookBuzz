# Quick Deploy Options

Two ways to get Book Buzz online immediately:

---

## Option 1: Railway + GitHub (Recommended)

**Easiest & Most Reliable**

- ✅ Auto-deploys from GitHub
- ✅ Free $5/month = several months hosting
- ✅ 24/7 uptime guaranteed
- ✅ One-click redeploy

**Setup time:** ~10 minutes

**Follow:** [DEPLOY_RAILWAY.md](./DEPLOY_RAILWAY.md)

---

## Option 2: Render (No GitHub Required)

**Simplest Setup, But Limited Free Tier**

### Quick Deploy

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Select "Public Git repository"
4. Paste this URL:
   ```
   https://github.com/YOUR_USERNAME/BookClub.git
   ```
   *(Or use the sample app first to test)*
5. Choose:
   - Environment: Python 3
   - Build command: `pip install -r requirements-web.txt && python extract_assets.py`
   - Start command: `python web_app.py`
6. Create Web Service

**Cost:** Free tier includes **750 free hours/month**
- That's ~31 days of 24/7 operation
- Spins down after 15 min of inactivity (wakes up in ~30 sec)

⚠️ **Note:** Render's free tier puts your app to sleep if unused. Good for 1-2 weeks, but not ideal for permanent hosting.

**Setup time:** ~5 minutes

---

## Option 3: Fly.io (Middle Ground)

**Good Free Tier, Excellent Uptime**

1. Go to https://fly.io
2. Sign up (free)
3. Install Fly CLI: https://fly.io/docs/getting-started/log-in-to-fly/
4. Run:
   ```bash
   fly launch
   fly deploy
   ```

**Free tier:** 3 shared-cpu-1x 256MB VMs
- Should handle Book Buzz easily
- 160GB/month egress (plenty)
- Good for continuous operation

**Setup time:** ~15 minutes

---

## Quick Comparison

| Service | Setup | Cost | Uptime | Best For |
|---------|-------|------|--------|----------|
| **Railway** | 10 min | Free $5/mo | 99.9% | Recommended |
| **Render** | 5 min | Free (limited) | 99% | Testing, 1-2 weeks |
| **Fly.io** | 15 min | Free tier | 99.9% | Medium-term hosting |

---

## My Recommendation

### For Testing (1-2 weeks):
Use **Render** — simplest setup, no GitHub needed

### For Permanent Hosting:
Use **Railway** — best free tier, auto-deploy, reliable

---

## Getting Your Public URL

After deployment, you'll receive a URL like:
```
https://bookbuzz-production.railway.app
https://bookbuzz.onrender.com
https://bookbuzz.fly.dev
```

**Share this URL** with anyone to access Book Buzz!

---

## Testing Locally First (Optional)

Before deploying, test it works:

```bash
# Windows
run_web.bat

# Mac/Linux
bash run_web.sh

# Then open: http://localhost:5000
```

If it works locally, it'll work in the cloud!

---

## Next Steps

1. **Choose a platform** (Railway recommended)
2. **Follow its deployment guide** (see links above)
3. **Get your public URL**
4. **Share it** with your book club!

---

**Any platform will work for at least 1-2 weeks guaranteed.** 🚀
