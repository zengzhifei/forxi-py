from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import time
import asyncio
import base64

from core.config import config
from modules.text2image.client import get_model_client, AVAILABLE_MODELS

router = APIRouter(prefix='/api/text2image', tags=['Text2Image'])


def process_async(func, *args):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, func, *args)


@router.post('/generate')
async def generate_image(
    prompt: str = Form(...),
    model: Optional[str] = Form('sdxl'),
    size: Optional[str] = Form('1024x1024'),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None)
):
    if not config.modelscope.api_token:
        raise HTTPException(status_code=500, detail='ModelScope API token not configured')
    
    if model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400, 
            detail=f'Invalid model. Available models: {list(AVAILABLE_MODELS.keys())}'
        )
    
    start_time = time.time()
    
    def generate():
        client = get_model_client(config.modelscope.api_token, model)
        return client.generate_and_download(
            prompt=prompt,
            size=size,
            negative_prompt=negative_prompt,
            seed=seed
        )
    
    result = await process_async(generate)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Image generation failed'))
    
    images = []
    for img_data in result.get('downloaded_images', []):
        if 'bytes' in img_data:
            img_base64 = base64.b64encode(img_data['bytes']).decode('utf-8')
            images.append({
                'base64': img_base64,
                'size': img_data['size']
            })
    
    return JSONResponse({
        'success': True,
        'message': 'Image generated successfully',
        'data': {
            'images': images,
            'model': result['model'],
            'prompt': result['prompt'],
            'size': result['size']
        },
        'process_time': round(time.time() - start_time, 2)
    })
