import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
STORIES_DIR = BASE_DIR / "stories"
FONTS_DIR = BASE_DIR / "fonts"
MUSIC_DIR = BASE_DIR / "music"

STORIES_DIR.mkdir(exist_ok=True)

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_MODEL = os.getenv("QWEN_MODEL", "deepseek-v4.1-flash")
QWEN_ENDPOINT = "https://token-plan.maas.qwencloudapi.com/compatible-mode/v1/chat/completions"

COMFYUI_URL = "http://127.0.0.1:8188"
IMG_WIDTH = 768
IMG_HEIGHT = 1344

FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg")
TITLE_FONT_PATH = os.getenv("TITLE_FONT_PATH", "C:/Windows/Fonts/arialbd.ttf")
CREEPSTER_FONT_PATH = FONTS_DIR / "Creepster-Regular.ttf"

EFFECTS = ["vhs_glitch", "film_grain", "static_noise", "scan_lines", "datamosh"]

VOICE_NAME = "ru-RU-SvetlanaNeural"
VOICE_RATE = "-15%"
