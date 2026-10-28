"""
Тест этапа 1: Генерация текста

Входные данные:
- topic (str): тема для генерации (опционально, по умолчанию генерируется автоматически)

Выходные данные:
- topic (str): тема рассказа
- title (str): название (1-2 слова)
- hashtags (str): хештеги для TikTok
- story (str): полный рассказ (~600 слов)
- image_prompt (str): промпт для генерации изображения

Использование:
    python scripts/test_stage1_text.py                    # автогенерация темы
    python scripts/test_stage1_text.py "заброшенная больница"  # указанная тема
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.text_generator import TextGenerator


async def main():
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = None

    print("=== Тест этапа 1: Генерация текста ===\n")
    
    gen = TextGenerator()
    
    if topic is None:
        print("1. Генерация темы...")
        topic = gen.generate_topic()
        print(f"   Тема: {topic}\n")
    else:
        print(f"1. Используем заданную тему: {topic}\n")

    print("2. Генерация названия...")
    title = gen.generate_title(topic)
    print(f"   Название: {title}\n")

    print("3. Генерация хештегов...")
    hashtags = gen.generate_hashtags(topic)
    print(f"   Хештеги: {hashtags}\n")

    print("4. Генерация рассказа...")
    story = gen.generate_story(topic)
    word_count = len(story.split())
    print(f"   Рассказ: {word_count} слов")
    print(f"   Превью: {story[:200]}...\n")

    print("5. Генерация промпта для изображения...")
    image_prompt = gen.generate_image_prompt(story, topic)
    print(f"   Промпт: {image_prompt}\n")

    print("=== Результаты ===")
    print(f"Тема: {topic}")
    print(f"Название: {title}")
    print(f"Хештеги: {hashtags}")
    print(f"Рассказ: {word_count} слов")
    print(f"Промпт изображения: {image_prompt[:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
