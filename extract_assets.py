import zipfile
import shutil
from pathlib import Path

def extract_all_assets():
    base_dir = Path(__file__).parent.resolve()
    assets_dir = base_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    sprites_zip = next(base_dir.glob("*Sprites*pack.zip"))
    ui_zip = next(base_dir.glob("*UI*Pack*pack.zip"))

    print("Extracting sprite pack...")
    with zipfile.ZipFile(sprites_zip, 'r') as z:
        for member in z.infolist():
            if not member.is_dir():
                parts = Path(member.filename).parts
                if len(parts) < 2:
                    continue
                target_path = assets_dir / "sprites" / Path(*parts[1:])
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(member) as source, open(target_path, "wb") as target:
                    shutil.copyfileobj(source, target)

    print("Extracting UI pack...")
    with zipfile.ZipFile(ui_zip, 'r') as z:
        for member in z.infolist():
            if not member.is_dir():
                parts = Path(member.filename).parts
                if len(parts) < 2:
                    continue
                target_path = assets_dir / "ui" / Path(*parts[1:])
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(member) as source, open(target_path, "wb") as target:
                    shutil.copyfileobj(source, target)

    print("Assets successfully extracted to:", assets_dir)

if __name__ == "__main__":
    extract_all_assets()
