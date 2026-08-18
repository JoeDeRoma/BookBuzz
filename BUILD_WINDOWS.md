# Building Book Buzz for Windows

## Prerequisites

1. **Python 3.10+** (install from [python.org](https://www.python.org/))
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Building the Windows Executable

### Option 1: Quick Build (Recommended)

Run the cross-platform build script:

```bash
python build_app.py
```

This will automatically:
- Extract asset packs
- Generate the app icon
- Build a standalone `.exe` file
- Output to `dist/BookBuzz.exe`

### Option 2: Manual PyInstaller Build

```bash
python -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name=BookBuzz ^
  --icon=bookclub.ico ^
  --add-data assets;assets ^
  --add-data bookclub.ico;. ^
  --hidden-import=PySide6 ^
  --hidden-import=pandas ^
  --hidden-import=numpy ^
  --hidden-import=PIL ^
  app.py
```

## Running the App

### Standalone Executable
Double-click `dist/BookBuzz.exe` to run the app.

### From Source (Development)
```bash
python app.py
```

## Troubleshooting

### SmartScreen Warning

Windows may show a security warning. Click:
- **More info** → **Run anyway**

### Missing DLL Error

Ensure Visual C++ Redistributable is installed:
- Download from [Microsoft](https://support.microsoft.com/en-us/help/2977003)
- Or install via: `pip install pyinstaller --upgrade`

### Asset Loading Errors

Extract assets manually:
```bash
python extract_assets.py
```

### Build Fails: "Access Denied"

Close any open instances of the app and delete `build/` and `dist/` folders:
```bash
rmdir /s build
rmdir /s dist
python build_app.py
```

## System Requirements

- Windows 7 or later
- 100 MB disk space for the executable
- Windows Defender/antivirus may slow initial launch (first run only)

## Distribution

The `.exe` is standalone and requires no installation:
- Copy to any directory
- Run directly
- No admin privileges needed (unless changing system settings)

---

**Need help?** Check the main [README.md](./README.md) or see [BUILD_MAC.md](./BUILD_MAC.md) for macOS build instructions.
