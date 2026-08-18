# Book Buzz Web Version

The easiest way to run Book Buzz! No installation needed for users — just open a browser.

## Quick Start

### 1. Install Dependencies (Builder's Machine)

```bash
pip install -r requirements-web.txt
```

### 2. Extract Assets (One-time)

```bash
python extract_assets.py
```

### 3. Start the Web Server

```bash
python web_app.py
```

You'll see:
```
============================================================
🎓 Book Buzz Web App Starting...
============================================================
📖 Open your browser to: http://localhost:5000
============================================================
```

### 4. Open in Browser

Click the link or go to: **http://localhost:5000**

## How to Use

1. **Load File** — Drag & drop a CSV or ZIP file with ballots
2. **Review Ballots** — See all submissions, compliance status
3. **Select Ballots** — Choose which ballots to include in analysis
4. **Run Analysis** — Click "Run Analysis" to calculate winner
5. **View Results** — See winner, standings, and head-to-head matchups
6. **Export** — Download results as CSV

## Sharing with Others

### On the Same Network

If someone is on the same WiFi/network:

1. Find your computer's IP address:
   - **Mac:** System Preferences → Network → copy IP
   - **Windows:** Open CMD, type `ipconfig`, look for "IPv4 Address"
   - **Linux:** Open terminal, type `hostname -I`

2. Start the server (see Step 3 above)

3. Share the link with others:
   ```
   http://YOUR_IP:5000
   ```

### On Different Networks (Easy Deployment)

Use a free service to share your local server:

**Option A: ngrok (Recommended)**
```bash
# Install: https://ngrok.com/download
ngrok http 5000
# Share the generated URL
```

**Option B: Heroku, Fly.io, or Railway (Free Tier)**
- Deploy the app to the cloud
- Get a public URL
- Share with anyone

## System Requirements

- **Python 3.8+** (on the builder's machine)
- **Any modern browser** (Chrome, Firefox, Safari, Edge)
- **No Python needed** on the user's machine!

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Troubleshooting

### Port Already in Use

If `localhost:5000` is already taken, edit `web_app.py` line at bottom:
```python
app.run(debug=False, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Assets Not Found

Run:
```bash
python extract_assets.py
```

### File Upload Issues

Ensure the file is a valid CSV or ZIP with proper ballot format.

## Features

✅ Drag & drop file upload  
✅ Ballot validation & compliance checking  
✅ Interactive ballot selection  
✅ Ranked Pairs (Condorcet) analysis  
✅ Winner & standings display  
✅ Head-to-head pairwise matrix  
✅ Export results to CSV  
✅ Mobile responsive design  
✅ Zero Python required for users  

## Next Steps

- **Deploy to Cloud:** Use Railway, Heroku, or Fly.io for free hosting
- **Share Public URL:** Get a permanent link anyone can access
- **Customize:** Modify templates/style.css for branding

---

**Enjoy Book Buzz! 📚**
