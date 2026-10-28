import asyncio
import json
import random
import shutil
import urllib.request
from pathlib import Path
from ..config import COMFYUI_URL, IMG_WIDTH, IMG_HEIGHT


class ImageGenerator:
    def __init__(self):
        self.comfyui_url = COMFYUI_URL
        self.width = IMG_WIDTH
        self.height = IMG_HEIGHT

    def _build_workflow(self, prompt: str) -> dict:
        return {
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["4", 1]}
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "juggernautXL_v8Rundiffusion.safetensors"}
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": self.width, "height": self.height, "batch_size": 1}
            },
            "6": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": random.randint(0, 2**32 - 1),
                    "steps": 20,
                    "cfg": 7.5,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["3", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "ugly, blurry, low quality, distorted, cartoon, anime, bright colors, happy, cheerful",
                    "clip": ["4", 1]
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["6", 0], "vae": ["4", 2]}
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "creepypasta", "images": ["8", 0]}
            }
        }

    async def generate(self, prompt: str, output_dir: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Промпт должен быть непустой строкой")
        
        output_dir = Path(output_dir)
        if not output_dir.exists():
            raise ValueError(f"Директория не существует: {output_dir}")

        workflow = self._build_workflow(prompt)
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(f"{self.comfyui_url}/prompt", data=data)
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        prompt_id = result['prompt_id']

        max_wait = 180
        waited = 0
        while waited < max_wait:
            req = urllib.request.Request(f"{self.comfyui_url}/history/{prompt_id}")
            response = urllib.request.urlopen(req)
            history = json.loads(response.read())
            
            if prompt_id in history:
                outputs = history[prompt_id].get('outputs', {})
                if '9' in outputs:
                    images = outputs['9'].get('images', [])
                    if images:
                        filename = images[0]['filename']
                        src = Path("ComfyUI/output") / filename
                        dst = output_dir / "image.png"
                        shutil.copy2(str(src), str(dst))
                        return str(dst)
            
            await asyncio.sleep(2)
            waited += 2
        
        raise TimeoutError("Превышено время ожидания генерации изображения (180 сек)")

    def generate_sync(self, prompt: str, output_dir: str) -> str:
        return asyncio.run(self.generate(prompt, output_dir))
