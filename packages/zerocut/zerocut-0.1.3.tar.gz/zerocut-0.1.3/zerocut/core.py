from PIL import Image

from typing import List

from .frame import Frame

def crop_and_fit(image, target_width, target_height):
    """Crop and resize an image to fit a target width and height while maintaining aspect ratio."""
    aspect_ratio = target_width / target_height
    img_width, img_height = image.size
    img_aspect = img_width / img_height

    # Calculate crop area (centered)
    if img_aspect > aspect_ratio:
        # If the image is wider, crop left and right
        new_width = int(img_height * aspect_ratio)
        left = (img_width - new_width) // 2
        box = (left, 0, left + new_width, img_height)
    else:
        # If the image is taller, crop top and bottom
        new_height = int(img_width / aspect_ratio)
        top = (img_height - new_height) // 2
        box = (0, top, img_width, top + new_height)

    cropped = image.crop(box)
    return cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)


class LifeCut:
    def __init__(self, images: List[Image.Image], frame: Frame):
        self.images = images
        self.frame = frame


    def create(self) -> Image.Image:
        """Creates a LifeCut image with the provided images and frame."""
        for idx, pos in enumerate(self.frame.positions):
            photo = self.images[idx].convert('RGB')
            fitted = crop_and_fit(photo, self.frame.width, self.frame.height)
            self.frame.frame_image.paste(fitted, pos, mask=fitted)

        return self.frame.frame_image