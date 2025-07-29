from PIL import Image

from ..frame import Frame

from importlib.resources import files


class SimpleWhiteFrame(Frame):
    def __init__(self):
        super().__init__(
            frame_image=Image.open(
                files("zerocut/frames/samples/white.png").joinpath("white.png")
            ).convert("RGB"),
            positions=[(64, 64), (64, 628), (64, 1192), (64, 1756)],
            photo_size=(876, 500),
        )


class SimpleBlackFrame(Frame):
    def __init__(self):
        super().__init__(
            frame_image=Image.open(
                files("zerocut/frames/samples/black.png").joinpath("black.png")
            ).convert("RGB"),
            positions=[(64, 64), (64, 628), (64, 1192), (64, 1756)],
            photo_size=(876, 500),
        )
