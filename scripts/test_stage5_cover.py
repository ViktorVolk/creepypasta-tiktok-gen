"""
Тест этапа 5: Создание обложек

Входные данные:
- image_path (str): путь к изображению (обязательно)
- title (str): название для обложки (обязательно)
- part_num (int): номер части (1, 2 или 3) (опционально, по умолчанию 1)
- output_path (str): путь для сохранения PNG файла (опционально, по умолчанию test_cover.png)

Выходные данные:
- output_path (str): путь к созданному PNG файлу обложки

Использование:
    python scripts/test_stage5_cover.py image.png "Темный дом"
    python scripts/test_stage5_cover.py image.png "Темный дом" 2 "output/cover2.png"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.cover_generator import CoverGenerator


def main():
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("ОШИБКА: Укажите путь к изображению")
        print("Использование: python scripts/test_stage5_cover.py <image_path> <title> [part_num] [output_path]")
        return
    
    if len(sys.argv) > 2:
        title = sys.argv[2]
    else:
        print("ОШИБКА: Укажите название")
        return
    
    if len(sys.argv) > 3:
        part_num = int(sys.argv[3])
    else:
        part_num = 1
    
    if len(sys.argv) > 4:
        output_path = sys.argv[4]
    else:
        output_path = "test_cover.png"

    print("=== Тест этапа 5: Создание обложек ===\n")
    print(f"Изображение: {image_path}")
    print(f"Название: {title}")
    print(f"Номер части: {part_num}")
    print(f"Выход: {output_path}\n")

    gen = CoverGenerator()
    
    print("Создание обложки...")
    try:
        result_path = gen.create(image_path, title, part_num, output_path)
        
        print(f"\n=== Результат ===")
        print(f"Обложка создана: {result_path}")
        
        if Path(result_path).exists():
            size = Path(result_path).stat().st_size
            print(f"Размер: {size / 1024 / 1024:.1f} MB")
        else:
            print("ОШИБКА: файл не создан!")
    except Exception as e:
        print(f"\nОШИБКА: {e}")


if __name__ == "__main__":
    main()
