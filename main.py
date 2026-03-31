from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import multiprocessing
import os
import time

# Use spawn to give worker processes a clean memory state (avoids fork+thread issues).
multiprocessing.set_start_method('spawn', force=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-9s %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

from core.file_utils import ensure_directories
from core import executor

# Worker process restarts after this many tasks, fully releasing onnxruntime arena memory.
# Lower = more frequent memory release, but adds ~2-3s model reload overhead per restart.
_WORKER_MAX_TASKS = 10

# Restart the worker pool after this many seconds of inactivity.
_IDLE_RESTART_SECONDS = 10


async def _idle_pool_manager():
    while True:
        await asyncio.sleep(30)
        t = executor.last_request_time
        if t > 0 and (time.time() - t) >= _IDLE_RESTART_SECONDS:
            executor.restart()
            executor.last_request_time = 0.0
            logger.info('[MEMORY] Worker pool restarted after idle, arena memory released')


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_directories()
    executor.init(_WORKER_MAX_TASKS)
    task = asyncio.create_task(_idle_pool_manager())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    executor.shutdown()


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
