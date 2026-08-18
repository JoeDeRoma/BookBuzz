import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    base_dir = Path(__file__).parent.resolve()
    assets_dir = base_dir / "assets"
    ico_path = base_dir / "bookclub.ico"
    app_py = base_dir / "app.py"

    if not assets_dir.exists():
        print("Extracting assets first...")
        from extract_assets import extract_all_assets
        extract_all_assets()

    if not ico_path.exists():
        print("Generating icon first...")
        from create_icon import generate_icon
        generate_icon()

    # Exclude unused heavy packages to make build fast and executable compact
    excluded_modules = [
        "matplotlib", "sqlalchemy", "geopandas", "playwright", "streamlit",
        "pyarrow", "scipy", "fastapi", "uvicorn", "torch", "IPython",
        "jupyter", "lxml", "docutils", "duckduckgo_search", "alembic",
        "altair", "pydeck", "primp", "pyogrio", "shapely", "cloudscraper"
    ]

    exclude_flags = []
    for mod in excluded_modules:
        exclude_flags.extend(["--exclude-module", mod])

    print("Building standalone one-file executable: dist/BookClub.exe ...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=BookClub",
        f"--icon={str(ico_path)}",
        f"--add-data={str(assets_dir)}{os.pathsep}assets",
        f"--add-data={str(base_dir / 'bookclub.ico')}{os.pathsep}.",
        "--hidden-import=PySide6",
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
    ] + exclude_flags + [str(app_py)]

    result = subprocess.run(cmd, cwd=str(base_dir))
    if result.returncode != 0:
        print("Build failed with return code:", result.returncode)
        sys.exit(result.returncode)

    exe_path = base_dir / "dist" / "BookClub.exe"
    print("\n" + "=" * 50)
    print("SUCCESS! Standalone Executable created:")
    print("Path:", exe_path)
    print(f"Size: {exe_path.stat().st_size / (1024 * 1024):.1f} MB")
    print("=" * 50)

if __name__ == "__main__":
    build_executable()
