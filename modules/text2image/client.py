import requests
import time
from typing import Optional, List
from PIL import Image
import io
import os
import json


class ModelScopeClient:
    def __init__(self, api_token: str, default_model: str = 'MusePublic/326_ckpt_SD_XL'):
        self.api_token = api_token
        self.default_model = default_model
        self.base_url = 'https://api-inference.modelscope.cn/v1/images/generations'
        self.task_url = 'https://api-inference.modelscope.cn/v1/tasks/'
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        size: str = '1024x1024',
        n: int = 1,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None
    ) -> dict:
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'X-ModelScope-Async-Mode': 'true'
        }
        
        payload = {
            'model': model or self.default_model,
            'prompt': prompt,
            'n': n,
            'size': size
        }
        
        if negative_prompt:
            payload['negative_prompt'] = negative_prompt
        if seed is not None:
            payload['seed'] = seed
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[ModelScope] Request payload: {payload}")
                response = requests.post(
                    self.base_url, 
                    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
                    headers=headers, 
                    timeout=120
                )
                print(f"[ModelScope] Response status: {response.status_code}")
                result = response.json()
                print(f"[ModelScope] Response: {result}")
                
                if 'task_id' in result:
                    task_id = result['task_id']
                    print(f"[ModelScope] Got task_id: {task_id}, polling for result...")
                    return self._poll_task(task_id, payload, prompt, size)
                
                if 'images' in result and result['images']:
                    return {
                        'success': True,
                        'images': result['images'],
                        'model': payload['model'],
                        'prompt': prompt,
                        'size': size
                    }
                
                if 'data' in result and result['data']:
                    images = []
                    for item in result['data']:
                        if 'url' in item:
                            images.append({'url': item['url']})
                    if images:
                        return {
                            'success': True,
                            'images': images,
                            'model': payload['model'],
                            'prompt': prompt,
                            'size': size
                        }
                
                if 'error' in result:
                    error_msg = result.get('error', 'Unknown error')
                    if 'loading' in str(error_msg).lower():
                        print(f"[ModelScope] Model loading, waiting... (attempt {attempt + 1})")
                        time.sleep(15)
                        continue
                    return {
                        'success': False,
                        'error': error_msg,
                        'detail': result
                    }
                
                if 'errors' in result:
                    return {
                        'success': False,
                        'error': result['errors'].get('message', 'API Error'),
                        'detail': result
                    }
                
                return {
                    'success': False,
                    'error': 'No task_id or images in response',
                    'detail': result
                }
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return {
                    'success': False,
                    'error': 'Request timeout'
                }
            except Exception as e:
                print(f"[ModelScope] Exception: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
        
        return {
            'success': False,
            'error': 'Max retries exceeded'
        }
    
    def _poll_task(self, task_id: str, payload: dict, prompt: str, size: str, max_wait: int = 180) -> dict:
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'X-ModelScope-Task-Type': 'image_generation'
        }
        
        poll_url = f'{self.task_url}{task_id}'
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                print(f"[ModelScope] Polling task: {poll_url}")
                response = requests.get(poll_url, headers=headers, timeout=30)
                print(f"[ModelScope] Poll response status: {response.status_code}")
                
                result = response.json()
                print(f"[ModelScope] Poll result: {result}")
                
                status = result.get('task_status', '')
                
                if status == 'SUCCEED':
                    images = []
                    if 'output_images' in result and result['output_images']:
                        for img_url in result['output_images']:
                            images.append({'url': img_url})
                    elif 'images' in result and result['images']:
                        for img in result['images']:
                            if isinstance(img, dict) and 'url' in img:
                                images.append({'url': img['url']})
                            elif isinstance(img, str):
                                images.append({'url': img})
                    
                    if images:
                        return {
                            'success': True,
                            'images': images,
                            'model': payload['model'],
                            'prompt': prompt,
                            'size': size
                        }
                    return {
                        'success': False,
                        'error': 'No images in result',
                        'detail': result
                    }
                
                if status == 'FAILED':
                    return {
                        'success': False,
                        'error': result.get('message', 'Task failed'),
                        'detail': result
                    }
                
                if status in ['PENDING', 'RUNNING', 'PROCESSING', '']:
                    time.sleep(5)
                    continue
                
                time.sleep(5)
                
            except Exception as e:
                print(f"[ModelScope] Poll exception: {e}")
                time.sleep(5)
        
        return {
            'success': False,
            'error': 'Polling timeout'
        }
    
    def download_image(self, url: str) -> bytes:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    
    def generate_and_download(
        self,
        prompt: str,
        model: Optional[str] = None,
        size: str = '1024x1024',
        n: int = 1,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None
    ) -> dict:
        result = self.generate(prompt, model, size, n, negative_prompt, seed)
        
        if not result['success']:
            return result
        
        downloaded_images = []
        for img_info in result['images']:
            try:
                img_url = img_info.get('url')
                if img_url:
                    img_bytes = self.download_image(img_url)
                    downloaded_images.append({
                        'url': img_url,
                        'bytes': img_bytes,
                        'size': len(img_bytes)
                    })
            except Exception as e:
                downloaded_images.append({
                    'url': img_info.get('url'),
                    'error': str(e)
                })
        
        result['downloaded_images'] = downloaded_images
        return result


AVAILABLE_MODELS = {
    'sdxl': 'MusePublic/326_ckpt_SD_XL',
    'pixel': 'MusePublic/484_ckpt_SD_XL',
}


def get_model_client(api_token: str, model_name: str = 'sdxl') -> ModelScopeClient:
    model = AVAILABLE_MODELS.get(model_name, AVAILABLE_MODELS['sdxl'])
    return ModelScopeClient(api_token, model)
