from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from core.file_utils import ensure_directories


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_directories()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title='AI Service API',
        description='AI Service',
        version='1.0.0',
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    
    from modules.image.router import router as image_router
    app.include_router(image_router)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(base_dir, 'uploads')
    if os.path.exists(upload_dir):
        app.mount('/uploads', StaticFiles(directory=upload_dir), name='uploads')
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    print('Starting AI Service API...')
    print('Using u2netp model (lightweight - optimized for 2GB RAM)')
    print('Server will be available at http://localhost:8000')
    print('API Documentation: http://localhost:8000/docs')
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)
