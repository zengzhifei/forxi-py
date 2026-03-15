import io
import os
import gc
from typing import Tuple, Optional
from PIL import Image
from rembg import remove, new_session


CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'models')
os.makedirs(CACHE_DIR, exist_ok=True)


class ImageProcessor:
    def __init__(self, max_size: int = 1024):
        self.max_size = max_size
        self._session = None
    
    def _get_session(self):
        if self._session is None:
            os.environ['U2NET_HOME'] = CACHE_DIR
            self._session = new_session(model_name='u2netp')
        return self._session
    
    def validate_file_size(self, file_size: int, max_size: int) -> bool:
        return file_size <= max_size
    
    def validate_content_type(self, content_type: str, allowed_types: list) -> bool:
        return content_type in allowed_types
    
    def compress(self, img: Image.Image) -> Image.Image:
        width, height = img.size
        if width > self.max_size or height > self.max_size:
            ratio = min(self.max_size / width, self.max_size / height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        return img
    
    def remove_background(self, image_bytes: bytes) -> bytes:
        session = self._get_session()
        input_image = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
        input_image = self.compress(input_image)
        output_image = remove(input_image, session=session)
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format='PNG')
        return output_buffer.getvalue()
    
    def crop_to_content(self, img: Image.Image, padding: int = 10) -> Image.Image:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        bbox = img.getbbox()
        if bbox:
            left, top, right, bottom = bbox
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = min(img.width, right + padding)
            bottom = min(img.height, bottom + padding)
            return img.crop((left, top, right, bottom))
        return img
    
    def crop_by_coordinates(self, img: Image.Image, x: int, y: int, width: int, height: int) -> Image.Image:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        left = max(0, x)
        top = max(0, y)
        right = min(img.width, x + width)
        bottom = min(img.height, y + height)
        return img.crop((left, top, right, bottom))
    
    def change_background(self, img: Image.Image, color: str) -> Image.Image:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        color = color.strip()
        if not color.startswith('#') or len(color) != 7:
            color = '#FFFFFF'
        
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        alpha = img.split()[3]
        bg = Image.new('RGBA', img.size, (r, g, b, 255))
        bg.paste(img, (0, 0), img)
        return bg
    
    def resize_for_photo(self, img: Image.Image, target_size: Tuple[int, int], crop: bool = True, padding: int = 20) -> Image.Image:
        if crop:
            img = self.crop_to_content(img, padding=padding)
        target_width, target_height = target_size
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * img_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        bg = Image.new('RGBA', target_size, (255, 255, 255, 255))
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        bg.paste(img, (paste_x, paste_y))
        return bg
    
    def create_photo(self, image_bytes: bytes, bg_color: str, target_size: Tuple[int, int]) -> bytes:
        session = self._get_session()
        input_image = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
        input_image = self.compress(input_image)
        
        no_bg = remove(input_image, session=session)
        input_image.close()
        
        no_bg = self.crop_to_content(no_bg, padding=10)
        
        if bg_color != '#FFFFFF':
            no_bg = self.change_background(no_bg, bg_color)
        
        final = self.resize_for_photo(no_bg, target_size, crop=False)
        
        output_buffer = io.BytesIO()
        final.save(output_buffer, format='PNG')
        result = output_buffer.getvalue()
        
        no_bg.close()
        final.close()
        output_buffer.close()
        gc.collect()
        
        return result


processor = ImageProcessor()
