"""
Проверка живучести всех компонентов пайплайна.

Проверяет:
- Qwen API (наличие ключа и возможность запроса)
- ComfyUI (доступность сервера)
- ffmpeg (наличие исполняемого файла)
- Edge TTS (возможность генерации голоса)
"""
import sys
import asyncio
import urllib.request
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import QWEN_API_KEY, QWEN_MODEL, QWEN_ENDPOINT, COMFYUI_URL, FFMPEG


def check_qwen_api():
    print("Проверка Qwen API...", end=" ")
    if not QWEN_API_KEY:
        print("ОШИБКА: QWEN_API_KEY не установлен в .env")
        return False
    
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {QWEN_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": QWEN_MODEL,
            "messages": [{"role": "user", "content": "Привет"}],
            "max_tokens": 5,
            "enable_thinking": False
        }
        response = requests.post(QWEN_ENDPOINT, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print("OK")
            return True
        else:
            print(f"ОШИБКА: статус {response.status_code}")
            return False
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False


def check_comfyui():
    print("Проверка ComfyUI...", end=" ")
    try:
        req = urllib.request.Request(f"{COMFYUI_URL}/system_stats")
        response = urllib.request.urlopen(req, timeout=5)
        if response.status == 200:
            print("OK")
            return True
        else:
            print(f"ОШИБКА: статус {response.status}")
            return False
    except Exception as e:
        print(f"ОШИБКА: {e}")
        print("   Убедитесь, что ComfyUI запущен: python ComfyUI\\main.py --listen")
        return False


def check_ffmpeg():
    print("Проверка ffmpeg...", end=" ")
    try:
        result = subprocess.run([FFMPEG, "-version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"OK ({version})")
            return True
        else:
            print("ОШИБКА: не удалось получить версию")
            return False
    except FileNotFoundError:
        print("ОШИБКА: ffmpeg не найден")
        print("   Установите: winget install Gyan.FFmpeg")
        return False
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False


async def check_edge_tts():
    print("Проверка Edge TTS...", end=" ")
    try:
        import edge_tts
        test_file = Path("test_tts.mp3")
        communicate = edge_tts.Communicate("Тест", "ru-RU-SvetlanaNeural")
        await communicate.save(str(test_file))
        if test_file.exists() and test_file.stat().st_size > 0:
            test_file.unlink()
            print("OK")
            return True
        else:
            print("ОШИБКА: файл не создан")
            return False
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False


def main():
    print("=== Проверка компонентов пайплайна ===\n")
    
    results = []
    results.append(("Qwen API", check_qwen_api()))
    results.append(("ComfyUI", check_comfyui()))
    results.append(("ffmpeg", check_ffmpeg()))
    results.append(("Edge TTS", asyncio.run(check_edge_tts())))
    
    print("\n=== Результаты ===")
    all_ok = True
    for name, status in results:
        status_str = "OK" if status else "ОШИБКА"
        print(f"{name:15s} {status_str}")
        if not status:
            all_ok = False
    
    if all_ok:
        print("\nВсе компоненты работают!")
    else:
        print("\nНекоторые компоненты не работают. Исправьте ошибки перед запуском пайплайна.")


if __name__ == "__main__":
    main()
