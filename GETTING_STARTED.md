# Book Buzz - Complete Guide

Choose the way you want to run Book Buzz:

## 🌐 **WEB VERSION** (Easiest for Sharing)

Perfect if you want to share with others on your network or the internet.

### Quick Start

#### Windows
```bash
run_web.bat
```

#### macOS/Linux
```bash
bash run_web.sh
```

Then open: **http://localhost:5000**

**Advantages:**
- ✅ Works on any device with a browser
- ✅ Easy to share on the same network
- ✅ Can deploy to the cloud (free options available)
- ✅ Mobile-friendly interface
- ✅ Zero installation for users

**See:** [README_WEB.md](./README_WEB.md) for detailed instructions

---

## 💻 **DESKTOP VERSION** (Windows/macOS)

For standalone installation on individual machines.

### macOS App Bundle

**For Developers:**
```bash
bash build_macos.sh
```

This creates: `dist/BookBuzz.app` (~180 MB, completely standalone)

**For Users:** Just double-click the `.app` to run. No Python needed!

**See:** [BUILD_MAC.md](./BUILD_MAC.md)

### Windows Executable

**For Developers:**
```bash
python build_exe.py
```

This creates: `dist/BookBuzz.exe` (~75 MB, completely standalone)

**For Users:** Just double-click the `.exe` to run. No Python needed!

**See:** [BUILD_WINDOWS.md](./BUILD_WINDOWS.md)

### Run from Source (Developers Only)

```bash
python app.py
```

Requires Python 3.8+ and all dependencies installed.

---

## 🚀 **Deployment Options**

### Option 1: Share on Same Network (Free, Instant)

Start the web server and share your computer's IP:

```bash
# Find your IP
ipconfig  # Windows
ifconfig  # macOS/Linux

# Share: http://YOUR_IP:5000
```

**Best for:** Local book club meetings, same building

---

### Option 2: Use ngrok (Free, 5 hours/month)

1. Download ngrok: https://ngrok.com/download
2. Start the web server: `python web_app.py`
3. In another terminal:
   ```bash
   ngrok http 5000
   ```
4. Share the generated URL

**Best for:** Quick temporary sharing

---

### Option 3: Deploy to Cloud (Free Tier Available)

Deploy `web_app.py` to:
- **Railway.app** (free $5/month credits)
- **Fly.io** (free tier available)
- **Heroku** (paid, but cheapest option)
- **Render** (free tier available)

**Best for:** Permanent hosting, accessible 24/7

---

## Choosing Your Approach

| Method | Setup Time | Users | Cost | Best For |
|--------|-----------|-------|------|----------|
| Web (Local) | 2 min | Same network | Free | Local meetings |
| Web + ngrok | 5 min | Anyone (5 hrs) | Free | Quick sharing |
| Web + Cloud | 30 min | Anyone, Always | Free-$5/mo | Permanent use |
| Desktop App | 15 min | One computer | Free | Personal use |
| Desktop App (shared) | 15 min | Manual install | Free | Distribution |

---

## System Requirements

### To Run Web Server (Developer)
- Python 3.8+
- ~500 MB disk space for dependencies
- Internet connection (for cloud deployment only)

### To Run Web App (Users)
- Any modern browser (Chrome, Firefox, Safari, Edge)
- **No Python needed!**
- Internet connection (if hosted on cloud)

### To Run Desktop App (Users)
- Windows 7+ OR macOS 10.13+
- ~200 MB disk space
- **No Python needed!**

---

## Quick Troubleshooting

### Web version won't start
```bash
# Re-extract assets
python extract_assets.py

# Check Python version
python --version  # Should be 3.8+

# Reinstall Flask
pip install Flask==2.3.3 Werkzeug==2.3.7
```

### Can't access web app from other device
1. Check firewall allows port 5000
2. Use the computer's actual IP (not localhost)
3. Verify both devices on same network

### Desktop app won't launch
- **Windows:** Run as Administrator
- **macOS:** Right-click → Open (if security warning)
- Remove quarantine: `xattr -d com.apple.quarantine BookBuzz.app`

---

## File Structure

```
BookClub/
├── web_app.py           # Web server
├── app.py               # Desktop app
├── run_web.bat          # Windows web launcher
├── run_web.sh           # Mac/Linux web launcher
├── build_exe.py         # Windows build script
├── build_macos.sh       # macOS build script
├── templates/           # Web HTML templates
├── static/              # Web CSS/JS assets
├── engine/              # Analysis logic
├── ui/                  # Desktop UI code
├── assets/              # Images, fonts, sprites
└── README_WEB.md        # Web version guide
```

---

## Next Steps

1. **Try the web version first:** Easy and universal
   ```bash
   run_web.bat  # or run_web.sh
   ```

2. **If you like it, consider deployment:**
   - Deploy to Railway/Fly.io for free hosting
   - Get a permanent shareable link

3. **For offline/standalone use:**
   - Build desktop app
   - Distribute `.app` or `.exe` to users

---

## Support

- **Web issues?** See [README_WEB.md](./README_WEB.md)
- **macOS app issues?** See [BUILD_MAC.md](./BUILD_MAC.md)
- **Windows app issues?** See [BUILD_WINDOWS.md](./BUILD_WINDOWS.md)

---

**Enjoy Book Buzz! 📚**
