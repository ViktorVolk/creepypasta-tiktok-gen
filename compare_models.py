import requests
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_ENDPOINT = "https://token-plan.maas.qwencloudapi.com/compatible-mode/v1/chat/completions"

OUTPUT_DIR = Path("compare")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_story(model: str, topic: str) -> str:
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Напиши хоррор-рассказ (крипипасту) для озвучки на 6 минут.

ТЕМА:
{topic}

ВАЖНО: Если в теме указаны конкретные детали (персонажи, место, события) - используй их, но не перегружай рассказ.

СТИЛЬ ПОВЕСТВОВАНИЯ:
- Пиши ПРОСТЫМ, РАЗГОВОРНЫМ языком, как будто рассказываешь другу
- НЕ перечисляй много деталей подряд - выбери 2-3 самых важных
- Пиши живо, эмоционально, с паузами для дыхания
- Запрещено: "следует отметить", "необходимо упомянуть", "стоит добавить"

СТРУКТУРА РАССКАЗА:
1. НАЧАЛО (около 100 слов): Начни с личной фразы (например: "Эта история произошла со мной, когда...", "Бабушка рассказывала мне, что...", "Я никогда не рассказывал никому, но..."). Кратко представь героя и место. Без лишних деталей.

2. РАЗВИТИЕ (около 200 слов): Опиши ОДНО-ДВА странных события. Не пытайся описать всё сразу. Дай читателю время осознать.

3. КУЛЬМИНАЦИЯ (около 200 слов): Опиши ГЛАВНОЕ страшное событие. Фокусируйся на одном эпизоде, а не на серии событий.

4. КОНЦОВКА (около 100 слов): Заверши историю. Финал должен быть ЗАВЕРШЁННЫМ, но с лёгкой недосказанностью. Не обрывай на полуслове.

ТРЕБОВАНИЯ:
- ОКОЛО 550-650 слов
- От ПЕРВОГО ЛИЦА (я, мне, мой)
- Естественный разговорный стиль
- Минимум деталей, максимум атмосферы

Рассказ:"""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2400,
        "temperature": 0.85
    }

    response = requests.post(QWEN_ENDPOINT, headers=headers, json=payload)
    result = response.json()

    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"[{model}] API error: {result}")


def main():
    if len(sys.argv) < 4:
        print("Использование: python compare_models.py <тема> <модель1> <модель2>")
        print()
        print("Пример:")
        print('  python compare_models.py "заброшенная школа" qwen3.8-flash qwen3.8-max')
        print()
        print("Доступные модели:")
        print("  qwen3.8-flash")
        print("  qwen3.8-max")
        print("  qwen3.7-flash")
        print("  qwen3.7-max")
        print("  qwen3.7-plus")
        sys.exit(1)

    topic = sys.argv[1]
    model1 = sys.argv[2]
    model2 = sys.argv[3]

    compare_dir = OUTPUT_DIR / f"{model1}_vs_{model2}"
    compare_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Сравнение моделей ===")
    print(f"Тема: {topic}")
    print(f"Модель 1: {model1}")
    print(f"Модель 2: {model2}")
    print(f"Папка: {compare_dir}\n")

    print(f"1. Генерация рассказа моделью [{model1}]...")
    story1 = generate_story(model1, topic)
    words1 = len(story1.split())
    (compare_dir / f"story_{model1}.txt").write_text(story1, encoding="utf-8")
    print(f"   Готово! {words1} слов\n")

    print(f"2. Генерация рассказа моделью [{model2}]...")
    story2 = generate_story(model2, topic)
    words2 = len(story2.split())
    (compare_dir / f"story_{model2}.txt").write_text(story2, encoding="utf-8")
    print(f"   Готово! {words2} слов\n")

    print("=== Результат ===")
    print(f"Папка: {compare_dir}")
    print()
    print(f"  {model1}: {words1} слов")
    print(f"  {model2}: {words2} слов")
    print()
    print(f"Файлы:")
    print(f"  story_{model1}.txt")
    print(f"  story_{model2}.txt")


if __name__ == "__main__":
    main()
