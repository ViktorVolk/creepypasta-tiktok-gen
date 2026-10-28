"""
Тест этапа 2: Генерация голоса (озвучка)

Входные данные:
- text (str): текст для озвучки (обязательно)
- output_path (str): путь для сохранения MP3 файла (опционально, по умолчанию test_voice.mp3)

Выходные данные:
- output_path (str): путь к созданному MP3 файлу

Использование:
    python scripts/test_stage2_voice.py "Привет, это тест озвучки"
    python scripts/test_stage2_voice.py "Текст для теста" "output/test.mp3"
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.voice_generator import VoiceGenerator


async def main():
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = "Это тестовый текст для проверки работы генератора голоса. Он должен быть озвучен русским женским голосом."
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = "test_voice.mp3"

    print("=== Тест этапа 2: Генерация голоса ===\n")
    print(f"Входной текст: {text}")
    print(f"Выходной файл: {output_path}\n")

    gen = VoiceGenerator()
    
    print("Генерация голоса...")
    result_path = await gen.generate(text, output_path)
    
    print(f"\n=== Результат ===")
    print(f"Файл создан: {result_path}")
    
    if Path(result_path).exists():
        size = Path(result_path).stat().st_size
        print(f"Размер: {size / 1024:.1f} KB")
    else:
        print("ОШИБКА: файл не создан!")


if __name__ == "__main__":
    asyncio.run(main())
