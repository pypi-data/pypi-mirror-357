from PIL import Image
from typing import List, Tuple


class Frame:
    def __init__(
        self,
        frame_image: Image.Image,
        positions: List[Tuple[int, int]],
        photo_size: Tuple[int, int],
    ):
        self.frame_image = frame_image
        self.positions = positions
        self.width, self.height = photo_size

    def __len__(self):
        return len(self.positions)

    def get_photo_box(self, index: int) -> Tuple[int, int, int, int]:
        """Returns (x1, y1, x2, y2) box for given image slot"""
        x, y = self.positions[index]
        return x, y, x + self.width, y + self.height
