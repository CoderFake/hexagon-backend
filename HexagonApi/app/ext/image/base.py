from dataclasses import dataclass, field
import io
from PIL import Image


@dataclass
class ImageContent:
    image: Image.Image

    @property
    def format(self) -> str:
        """
        Gets the image format string interpreted by PIL.

        https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
        """
        return self.image.format or ""

    @property
    def mime(self) -> str:
        """
        Gets the MIME type of the image.
        """
        return Image.MIME.get(self.format, 'application/octet-stream')

    @property
    def ext(self) -> str:
        """
        Gets the extension of the image file.
        """
        return self.format.lower()

    def bytes(self, format: str | None = None) -> bytes:
        """
        Gets the image data.
        """
        buf = io.BytesIO()
        self.image.save(buf, format=format or self.format)
        return buf.getvalue()


def load_image(data: bytes) -> ImageContent:
    """
    Interprets the image data.
    """
    image = Image.open(io.BytesIO(data))
    image = resize_and_compress_image(image=image, max_width=150, max_height=200)
    return ImageContent(image)


def resize_and_compress_image(image_path: str = None, image: Image = None, max_width=None, max_height=None, quality=85):
    """
    Resize and compress an image, returning the processed Image object.

    :param image_path: Path to the original image (optional if 'image' is provided)
    :param image: A PIL Image object (optional if 'image_path' is provided)
    :param max_width: Maximum width for resizing (optional)
    :param max_height: Maximum height for resizing (optional)
    :param quality: Compression quality for JPEG (default is 85)
    :return: Processed Image object after resizing and compression
    :raises ValueError: If both 'image_path' and 'image' are provided or if neither is provided
    """
    
    if image_path and image:
        raise ValueError("Both 'image_path' and 'image' cannot be provided. Please provide only one.")
    
    if image_path:
        img = Image.open(image_path)
    elif image:
        img = image
    else:
        raise ValueError("Either 'image_path' or 'image' must be provided")

    if max_width is not None or max_height is not None:
        img.thumbnail((max_width, max_height)) 

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img_io = io.BytesIO()
    img.save(img_io, format="JPEG", quality=quality)
    img_io.seek(0) 

    optimized_img = Image.open(img_io)
    
    return optimized_img


def resolve_exif(img: Image.Image) -> Image.Image:
    """
    Applies the rotation information contained in Exif.
    """
    exif = img.getexif()
    if exif is None:
        return img

    orientation = exif.get(274, None)

    match orientation:
        case 1:
            img = img
        case 2:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        case 3:
            img = img.transpose(Image.ROTATE_180)
        case 4:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        case 5:
            img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
        case 6:
            img = img.transpose(Image.ROTATE_270)
        case 7:
            img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        case 8:
            img = img.transpose(Image.ROTATE_90)
        case _:
            img = img

    new_img = Image.new(img.mode, img.size)
    new_img.putdata(img.getdata())

    return new_img
