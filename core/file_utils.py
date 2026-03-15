import os
import uuid
import aiofiles
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
STATIC_URL = '/uploads'


def ensure_directories():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def generate_filename(extension: str = 'png') -> str:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f'{timestamp}_{unique_id}.{extension}'


async def save_file(content: bytes, filename: str) -> str:
    ensure_directories()
    filepath = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(content)
    return f'{STATIC_URL}/{filename}'


def get_file_path(filename: str) -> str:
    return os.path.join(UPLOAD_DIR, filename)
