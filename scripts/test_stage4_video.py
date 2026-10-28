"""
Тест этапа 4: Генерация видео

Входные данные:
- image_path (str): путь к изображению (обязательно)
- audio_path (str): путь к аудио файлу (обязательно)
- output_path (str): путь для сохранения MP4 файла (опционально, по умолчанию test_video.mp4)
- effect (str): название эффекта (опционально, по умолчанию случайный)

Доступные эффекты:
- vhs_glitch - VHS полосы + искажение цвета
- film_grain - зернистость плёнки
- static_noise - белый шум
- scan_lines - линии развёртки
- datamosh - цифровое растекание

Выходные данные:
- output_path (str): путь к созданному MP4 файлу

Использование:
    python scripts/test_stage4_video.py image.png audio.mp3
    python scripts/test_stage4_video.py image.png audio.mp3 output.mp4 vhs_glitch
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.video_generator import VideoGenerator
from src.config import EFFECTS


def main():
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("ОШИБКА: Укажите путь к изображению")
        print("Использование: python scripts/test_stage4_video.py <image_path> [audio_path] [output_path] [effect]")
        return
    
    if len(sys.argv) > 2:
        audio_path = sys.argv[2]
    else:
        print("ОШИБКА: Укажите путь к аудио файлу")
        return
    
    if len(sys.argv) > 3:
        output_path = sys.argv[3]
    else:
        output_path = "test_video.mp4"
    
    if len(sys.argv) > 4:
        effect = sys.argv[4]
    else:
        effect = None

    print("=== Тест этапа 4: Генерация видео ===\n")
    print(f"Изображение: {image_path}")
    print(f"Аудио: {audio_path}")
    print(f"Выход: {output_path}")
    print(f"Эффект: {effect if effect else 'случайный'}")
    print(f"Доступные эффекты: {EFFECTS}\n")

    gen = VideoGenerator()
    
    print("Генерация видео...")
    try:
        result_path = gen.create(image_path, audio_path, output_path, effect)
        
        print(f"\n=== Результат ===")
        print(f"Видео создано: {result_path}")
        
        if Path(result_path).exists():
            size = Path(result_path).stat().st_size
            print(f"Размер: {size / 1024 / 1024:.1f} MB")
        else:
            print("ОШИБКА: файл не создан!")
    except Exception as e:
        print(f"\nОШИБКА: {e}")


if __name__ == "__main__":
    main()
