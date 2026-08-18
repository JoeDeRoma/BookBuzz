# How to Run Book Buzz on Mac

## Option 1: Simple One-Click App (Easiest)

Your friend will need to have Python 3 installed (most Macs do). If not, they can install it here: https://www.python.org/downloads/

**Steps:**

1. You send them the `BookBuzz.app` folder (or the entire BookClub project folder)
2. They open Finder and find the `BookBuzz.app` file
3. They double-click `BookBuzz.app`
4. A browser window opens automatically with Book Buzz ready to use
5. Upload CSV files and run analysis as usual

**That's it!** No terminal, no commands needed.

---

## Building the App from Source

If you need to build `BookBuzz.app` yourself:

1. On a Mac, open Terminal
2. Navigate to the BookClub folder:
   ```
   cd /path/to/BookClub
   ```
3. Run the build script:
   ```
   bash build_mac_web.sh
   ```
4. Wait 2-3 minutes while it installs dependencies
5. A folder called `build_mac_web` will be created
6. Inside it, you'll see `BookBuzz.app`
7. Zip this folder or drag it into Dropbox/Google Drive to share with your friend

---

## Troubleshooting

**If it doesn't open:**
- Make sure Python 3 is installed (run `python3 --version` in Terminal)
- Try right-clicking `BookBuzz.app` → Open
- Check that the app has execute permissions (it should)

**If the browser doesn't open automatically:**
- Open a browser manually and go to `http://localhost:5000`

**To stop the app:**
- Close the browser or press `Ctrl+C` in Terminal (if running from Terminal)

---

## For Windows Users

Use `BookBuzz.exe` instead (built from `build_app.py`)

For web version on Windows, run:
```
python run_web.bat
```

## For Linux Users

Run:
```
bash run_web.sh
```

---

## Questions?

The app is a web-based ballot analysis tool. Upload a CSV file with ballots and it will analyze them using the Ranked Pairs (Tideman Condorcet) voting method.
