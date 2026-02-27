from PIL import Image, ImageDraw
from pathlib import Path

class ShotChart:
    def __init__(self) -> None:
        # Ruta absoluta al directori on està aquest fitxer
        self.base_dir = Path(__file__).resolve().parent

        # court.png és un asset del projecte (read-only)
        self.court_path = self.base_dir / "court.png"

        # tmp és on guardem resultats (writable)
        self.tmp_dir = self.base_dir / "tmp"
        self.tmp_dir.mkdir(exist_ok=True)

        self.img = Image.open(self.court_path).copy()
        self.img_draw = ImageDraw.Draw(self.img)

    def add_made(self, x, y):
        self.img_draw.ellipse(
            [(x - 2, y - 2), (x + 2, y + 2)],
            outline="black",
            width=1
        )

    def add_miss(self, x, y):
        self.img_draw.text((x - 5, y - 5), "X")

    def save(self, filename: str):
        self.img.save(self.tmp_dir / filename)