# Building Book Buzz for macOS

## What You Get

The build process creates a **standalone `.app` bundle** — just like any app you download from the App Store. No Python installation needed on the user's machine.

## Prerequisites (Builder's Machine Only)

1. **macOS 10.13+** (High Sierra or later)
2. **Python 3.10+** — Install via Homebrew:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install python3
   ```

## Building the macOS App

### Quickest Method: Run the Build Script

On your Mac, open Terminal and run:

```bash
cd /path/to/BookClub
bash build_macos.sh
```

This automatically:
- ✅ Creates a Python virtual environment
- ✅ Installs all dependencies
- ✅ Extracts asset packs
- ✅ Generates the app icon
- ✅ Builds a self-contained `.app` bundle
- ✅ Outputs to `dist/BookBuzz.app`

The script will show you the app size and location when complete.

### Manual Build (If Preferred)

```bash
# Install dependencies
pip3 install PyInstaller PySide6 pandas numpy pillow

# Extract assets
python3 extract_assets.py

# Generate icon
python3 create_icon.py

# Build the app
python3 -m PyInstaller \
  --noconfirm \
  --onedir \
  --windowed \
  --name=BookBuzz \
  --icon=bookclub.ico \
  --add-data=assets:assets \
  --add-data=bookclub.ico:. \
  --hidden-import=PySide6 \
  --hidden-import=pandas \
  --hidden-import=numpy \
  --hidden-import=PIL \
  --osx-bundle-identifier=com.bookbuzz.app \
  --codesign-identity=- \
  app.py
```

## Running the App

### To Run Locally
```bash
open dist/BookBuzz.app
```

### To Install System-Wide
```bash
# Move to Applications folder
mv dist/BookBuzz.app /Applications/

# Then launch like any other app (Spotlight search: cmd+space, type "BookBuzz")
```

### To Share with Others
The `dist/BookBuzz.app` bundle is completely self-contained. You can:
- 📧 Email it to someone
- ☁️ Upload to cloud storage (Google Drive, Dropbox, etc.)
- 💾 Copy to a USB drive
- Share via any file transfer method

**No Python needed on the recipient's machine!**

## Troubleshooting

## Troubleshooting

If you see this when opening the app on a different Mac:

**Quick Fix:**
```bash
xattr -d com.apple.quarantine /path/to/BookBuzz.app
```

**Or allow it in Security Settings:**
- Open System Preferences → Security & Privacy → General
- Click "Open Anyway" next to the BookBuzz warning

### "Cannot open because the developer cannot be verified" (Apple Silicon Macs)

This is normal for unsigned apps. Click "Open" in the security prompt, or:
```bash
sudo spctl --add /Applications/BookBuzz.app
```bash

```

Try rebuilding with verbose output:
```bash
bash build_macos.sh 2>&1 | tee build.log
```bash

```

### Assets Not Loading

Manually extract:
```bash
python3 extract_assets.py
```

## System Requirements

- **macOS:** 10.13 (High Sierra) or later
- **Processor:** Intel or Apple Silicon (M1/M2/M3+)
- **Disk Space:** ~150–200 MB for the app bundle
- **RAM:** 512 MB minimum

## Sharing Your Built App

The `.app` bundle is completely standalone and portable:

1. **Via Email:** Compress first (if > 25 MB):
   ```bash
   cd dist && zip -r BookBuzz.app.zip BookBuzz.app
   ```

2. **Via Cloud Storage:** Upload `dist/BookBuzz.app` directly to Dropbox, Google Drive, iCloud, etc.

3. **Via USB Drive:** Copy `dist/BookBuzz.app` to a USB drive

4. **Via Web Server:** Host the `.app` or `.zip` for download

Recipients just need to:
- Download the `.app`
- Move to `/Applications` (optional)
- Double-click to run (no Python, no installation needed!)

## Building for Distribution

For professional distribution, consider:
- **Code signing** your app (optional, for removing security warnings)
- **Notarizing** with Apple (optional, for maximum trust)
- Contact Apple Developer Program for details

---

**Need help?** Check the main [README.md](./README.md) or see [BUILD_WINDOWS.md](./BUILD_WINDOWS.md) for Windows build instructions.
