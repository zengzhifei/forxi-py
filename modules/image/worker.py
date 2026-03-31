"""Top-level functions executed in the subprocess worker.
Must be module-level (not nested/lambda) to be picklable by multiprocessing.
"""
import io
from PIL import Image


def run_remove_background(image_bytes: bytes) -> bytes:
    from modules.image.processor import processor
    return processor.remove_background(image_bytes)


def run_create_photo(image_bytes: bytes, bg_color: str, target_size: tuple) -> bytes:
    from modules.image.processor import processor
    return processor.create_photo(image_bytes, bg_color, target_size)


def run_crop(contents: bytes, x, y, width, height) -> tuple:
    from modules.image.processor import processor, _trim_memory
    img = Image.open(io.BytesIO(contents)).convert('RGBA')
    img = processor.compress(img)
    if x is not None and y is not None and width is not None and height is not None:
        cropped = processor.crop_by_coordinates(img, x, y, width, height)
    else:
        cropped = processor.crop_to_content(img, padding=10)
    output_buffer = io.BytesIO()
    cropped.save(output_buffer, format='PNG')
    result_bytes = output_buffer.getvalue()
    w, h = cropped.width, cropped.height
    img.close()
    cropped.close()
    output_buffer.close()
    _trim_memory()
    return result_bytes, w, h
