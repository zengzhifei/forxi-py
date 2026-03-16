import os
from pydantic import BaseModel


class ImageConfig(BaseModel):
    max_size: int = 1024
    max_file_size: int = 5 * 1024 * 1024
    allowed_types: list = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']


class Config:
    image = ImageConfig()


config = Config()
