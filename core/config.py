import os
from typing import Optional
from pydantic import BaseModel


class ImageConfig(BaseModel):
    max_size: int = 1024
    max_file_size: int = 5 * 1024 * 1024
    allowed_types: list = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']


class ServerConfig(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000
    workers: int = 1


class ModelScopeConfig(BaseModel):
    api_token: Optional[str] = None
    default_model: str = 'sdxl'
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.api_token is None:
            self.api_token = os.getenv('MODELSCOPE_API_TOKEN')


class Config:
    image = ImageConfig()
    server = ServerConfig()
    modelscope = ModelScopeConfig()


config = Config()
