"""
Тест этапа 3: Генерация изображения

Входные данные:
- prompt (str): промпт для генерации изображения на английском (обязательно)
- output_dir (str): директория для сохранения (опционально, по умолчанию текущая)

Выходные данные:
- image_path (str): путь к созданному PNG файлу

Требования:
- ComfyUI должен быть запущен: python ComfyUI\\main.py --listen

Использование:
    python scripts/test_stage3_image.py "dark horror house, fog, night, cinematic"
    python scripts/test_stage3_image.py "abandoned hospital, dark corridor" "output/"
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.image_generator import ImageGenerator


async def main():
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = "dark abandoned house, fog, night, horror atmosphere, cinematic lighting, eerie, portrait orientation"
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "."

    print("=== Тест этапа 3: Генерация изображения ===\n")
    print(f"Промпт: {prompt}")
    print(f"Директория: {output_dir}\n")

    gen = ImageGenerator()
    
    print("Генерация изображения (может занять до 3 минут)...")
    result_path = await gen.generate(prompt, output_dir)
    
    print(f"\n=== Результат ===")
    print(f"Изображение создано: {result_path}")
    
    if Path(result_path).exists():
        size = Path(result_path).stat().st_size
        print(f"Размер: {size / 1024 / 1024:.1f} MB")
    else:
        print("ОШИБКА: файл не создан!")


if __name__ == "__main__":
    asyncio.run(main())
