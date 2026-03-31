from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import asyncio
import base64
import time

from core.config import config
from core import executor
from modules.image import worker
from modules.image.processor import processor

router = APIRouter(prefix='/api/image', tags=['Image'])


@router.post('/remove-background')
async def remove_background(file: UploadFile = File(...)):
    contents = await file.read()

    if not processor.validate_file_size(len(contents), config.image.max_file_size):
        raise HTTPException(status_code=413, detail=f'File size exceeds {config.image.max_file_size // 1024 // 1024}MB limit')

    if not processor.validate_content_type(file.content_type, config.image.allowed_types):
        raise HTTPException(status_code=400, detail='Invalid image file type')

    start_time = time.time()
    loop = asyncio.get_event_loop()
    result_bytes = await loop.run_in_executor(executor.get(), worker.run_remove_background, contents)
    executor.record_request()
    img_base64 = base64.b64encode(result_bytes).decode('utf-8')

    return JSONResponse({
        'success': True,
        'message': 'Background removed',
        'data': {'base64': img_base64, 'size': len(result_bytes)},
        'process_time': round(time.time() - start_time, 2)
    })


@router.post('/transparent')
async def make_transparent(file: UploadFile = File(...)):
    contents = await file.read()

    if not processor.validate_file_size(len(contents), config.image.max_file_size):
        raise HTTPException(status_code=413, detail=f'File size exceeds {config.image.max_file_size // 1024 // 1024}MB limit')

    if not processor.validate_content_type(file.content_type, config.image.allowed_types):
        raise HTTPException(status_code=400, detail='Invalid image file type')

    start_time = time.time()
    loop = asyncio.get_event_loop()
    result_bytes = await loop.run_in_executor(executor.get(), worker.run_remove_background, contents)
    executor.record_request()
    img_base64 = base64.b64encode(result_bytes).decode('utf-8')

    return JSONResponse({
        'success': True,
        'message': 'Transparent background created',
        'data': {'base64': img_base64, 'size': len(result_bytes)},
        'process_time': round(time.time() - start_time, 2)
    })


@router.post('/crop')
async def crop_image(
    file: UploadFile = File(...),
    x: Optional[int] = Form(None),
    y: Optional[int] = Form(None),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None)
):
    contents = await file.read()

    if not processor.validate_file_size(len(contents), config.image.max_file_size):
        raise HTTPException(status_code=413, detail=f'File size exceeds {config.image.max_file_size // 1024 // 1024}MB limit')

    if not processor.validate_content_type(file.content_type, config.image.allowed_types):
        raise HTTPException(status_code=400, detail='Invalid image file type')

    start_time = time.time()
    loop = asyncio.get_event_loop()
    result_bytes, result_width, result_height = await loop.run_in_executor(
        executor.get(), worker.run_crop, contents, x, y, width, height
    )
    executor.record_request()
    img_base64 = base64.b64encode(result_bytes).decode('utf-8')

    response_data = {
        'base64': img_base64,
        'size': len(result_bytes),
        'width': result_width,
        'height': result_height
    }
    if x is not None and y is not None and width is not None and height is not None:
        response_data['crop_params'] = {'x': x, 'y': y, 'width': width, 'height': height}

    return JSONResponse({
        'success': True,
        'message': 'Image cropped',
        'data': response_data,
        'process_time': round(time.time() - start_time, 2)
    })


@router.post('/photo')
async def create_photo(
    file: UploadFile = File(...),
    bg_color: Optional[str] = Form('#FFFFFF'),
    width: Optional[int] = Form(300),
    height: Optional[int] = Form(400)
):
    contents = await file.read()

    if not processor.validate_file_size(len(contents), config.image.max_file_size):
        raise HTTPException(status_code=413, detail=f'File size exceeds {config.image.max_file_size // 1024 // 1024}MB limit')

    if not processor.validate_content_type(file.content_type, config.image.allowed_types):
        raise HTTPException(status_code=400, detail='Invalid image file type')

    start_time = time.time()
    loop = asyncio.get_event_loop()
    result_bytes = await loop.run_in_executor(
        executor.get(), worker.run_create_photo, contents, bg_color, (width, height)
    )
    executor.record_request()
    img_base64 = base64.b64encode(result_bytes).decode('utf-8')

    return JSONResponse({
        'success': True,
        'message': 'Photo created',
        'data': {'base64': img_base64, 'size': len(result_bytes), 'width': width, 'height': height, 'bg_color': bg_color},
        'process_time': round(time.time() - start_time, 2)
    })
