from PIL import Image

from ..frame import Frame


class SimpleWhiteFrame(Frame):
    def __init__(self):
        super().__init__(
            frame_image=Image.open("zerocut/frames/samples/white.png").convert("RGBA"),
            positions=[
                (64, 64), (64, 628), (64, 1192), (64, 1756)
            ],
            photo_size=(876, 500)
        )



class SimpleBlackFrame(Frame):
    def __init__(self):
        super().__init__(
            frame_image=Image.open("zerocut/frames/samples/black.png").convert("RGBA"),
            positions=[
                (64, 64), (64, 628), (64, 1192), (64, 1756)
            ],
            photo_size=(876, 500)
        )
