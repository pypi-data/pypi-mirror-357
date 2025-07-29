from PIL import Image

import os

from ..frame import Frame


class SimpleWhiteFrame(Frame):
    def __init__(self):
        super().__init__(
            frame_image=Image.open(os.path.join(os.path.dirname(__file__), "samples", "white.png")).convert("RGB"),
            positions=[(64, 64), (64, 628), (64, 1192), (64, 1756)],
            photo_size=(876, 500),
        )


class SimpleBlackFrame(Frame):
    def __init__(self):
        super().__init__(
            frame_image=Image.open(os.path.join(os.path.dirname(__file__), "samples", "black.png")).convert("RGB"),
            positions=[(64, 64), (64, 628), (64, 1192), (64, 1756)],
            photo_size=(876, 500),
        )
