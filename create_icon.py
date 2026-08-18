from PIL import Image
from pathlib import Path

def generate_icon():
    base_dir = Path(__file__).parent.resolve()
    assets_dir = base_dir / "assets"
    
    # Extract chicken frame for the app icon
    chicken_sheet = assets_dir / "sprites" / "Characters" / "Free Chicken Sprites.png"
    if chicken_sheet.exists():
        img = Image.open(chicken_sheet)
        # Crop first 16x16 frame
        frame = img.crop((0, 0, 16, 16))
        # Resize to standard icon sizes using nearest neighbor
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        frames = [frame.resize(size, Image.Resampling.NEAREST) for size in icon_sizes]
        
        ico_path = base_dir / "bookclub.ico"
        frames[0].save(
            str(ico_path),
            format="ICO",
            sizes=icon_sizes,
            append_images=frames[1:]
        )
        print("Generated app icon:", ico_path)

if __name__ == "__main__":
    generate_icon()
