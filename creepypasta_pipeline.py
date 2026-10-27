import asyncio
import edge_tts
import requests
import json
import os
import random
import subprocess
import time
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path("stories")
OUTPUT_DIR.mkdir(exist_ok=True)
FONTS_DIR = Path("fonts")
FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg")
TITLE_FONT_PATH = os.getenv("TITLE_FONT_PATH", "C:/Windows/Fonts/arialbd.ttf")

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_MODEL = os.getenv("QWEN_MODEL", "deepseek-v4.1-flash")
QWEN_ENDPOINT = "https://token-plan.maas.qwencloudapi.com/compatible-mode/v1/chat/completions"

COMFYUI_URL = "http://127.0.0.1:8188"
IMG_WIDTH = 768
IMG_HEIGHT = 1344

EFFECTS = ["vhs_glitch", "film_grain", "static_noise", "scan_lines", "datamosh"]


def qwen_request(prompt, max_tokens=400, temperature=0.85):
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": QWEN_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    response = requests.post(QWEN_ENDPOINT, headers=headers, json=payload)
    result = response.json()
    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"Qwen API error: {result}")


async def generate_topic() -> str:
    prompt = """Придумай уникальную и жуткую тему для хоррор-рассказа (крипипасты).

Требования:
- 1-2 предложения с описанием темы
- Избегай клише (заброшенные больницы, темные леса)
- НЕ пиши префикс "Тема:" в ответе

Ответ (без префикса "Тема:"):"""
    result = qwen_request(prompt, max_tokens=100, temperature=0.95)
    result = result.replace("Тема:", "").replace("тема:", "").strip()
    return result


async def generate_title(topic: str) -> str:
    prompt = f"""Придумай короткое название для хоррор-рассказа (крипипасты) на 1-2 слова.

ТЕМА/ПОЖЕЛАНИЯ:
{topic}

Требования:
- Только 1-2 слова
- Жуткое, запоминающееся
- На русском языке
- Отражает суть темы
- БЕЗ кавычек, без пояснений, ТОЛЬКО название

Название:"""
    result = qwen_request(prompt, max_tokens=20, temperature=0.9)
    
    # Очистка результата
    result = result.replace('"', '').replace("'", '').replace('«', '').replace('»', '').strip()
    result = result.replace('Название:', '').replace('название:', '').strip()
    
    # Если пусто - используем тему
    if not result:
        result = topic[:10]
    
    return result


async def generate_hashtags(topic: str) -> str:
    prompt = f"""Подбери 7-8 популярных хештегов для TikTok на основе темы хоррор-рассказа.

ТЕМА:
{topic}

Требования:
- Формат: #хештег через пробел
- Микс популярных (#хоррор #крипипаста #страх #страшныеистории) и тематических
- ВСЕ хештеги на русском языке
- ТОЛЬКО хештеги, без пояснений

Хештеги:"""
    return qwen_request(prompt, max_tokens=200, temperature=0.7)


async def generate_story(topic: str) -> str:
    prompt = f"""Напиши хоррор-рассказ (крипипасту) для озвучки на 6 минут.

ТЕМА:
{topic}

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА ФОРМАТИРОВАНИЯ:
- НЕ добавляй никаких комментариев перед рассказом (никаких "Вот история", "Постарался сделать" и т.д.)
- НЕ обрамляй текст звездочками, кавычками или другими символами
- Выводи ТОЛЬКО текст рассказа, ничего больше
- Начинай сразу с первой фразы рассказа

СТИЛЬ ПОВЕСТВОВАНИЯ:
- Пиши СДЕРЖАННЫМ, СПОКОЙНЫМ тоном, как будто вспоминаешь прошлые события
- Избегай сленга, жаргонизмов, восклицаний
- НЕ используй фразы: "слушай", "ору", "реально очканул", "прикинь", "короче"
- Пиши литературным языком, но простым и понятным
- Пиши размеренно, с паузами, без суеты
- Запрещено: "следует отметить", "необходимо упомянуть", "стоит добавить"

ТРЕБОВАНИЯ:
- ОКОЛО 550-650 слов
- От ПЕРВОГО ЛИЦА (я, мне, мой)
- Сдержанный, спокойный стиль повествования
- Минимум деталей, максимум атмосферы

Рассказ:"""
    return qwen_request(prompt, max_tokens=2400, temperature=0.85)


async def generate_voice(text: str, output_file: str):
    voice = "ru-RU-SvetlanaNeural"
    communicate = edge_tts.Communicate(text, voice, rate="-15%")
    await communicate.save(output_file)
    print(f"   Голос сохранен: {output_file}")


async def generate_image_prompt(story: str, topic: str) -> str:
    prompt = f"""Создай описание для генерации изображения по теме рассказа.

РАССКАЗ:
{story}

Создай промпт для SDXL на английском языке (50 слов):
- Опиши ГЛАВНОЕ МЕСТО действия из рассказа (дом, лес, больница и т.д.)
- Опиши АТМОСФЕРУ (темнота, туман, заброшенность, жуткое освещение)
- Опиши ГЛАВНЫЙ УЖАС/МОНСТРА/АНОМАЛИЮ, на фото оно должно выглядеть жутко и уродливо
- Добавь детали: тени, силуэты, странные формы на заднем плане
- Стиль: photorealistic, horror, cinematic lighting, dark atmosphere, eerie
- ВАЖНО: вертикальная композиция (portrait orientation), объект съёмки в центре кадра

Промпт на английском:"""
    return qwen_request(prompt, max_tokens=300, temperature=0.7)


async def generate_image(prompt: str, output_dir: Path) -> str:
    workflow = {
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
            "inputs": {"width": IMG_WIDTH, "height": IMG_HEIGHT, "batch_size": 1}
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "seed": random.randint(0, 2**32 - 1),
                "steps": 20, "cfg": 7.5,
                "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
                "model": ["4", 0], "positive": ["3", 0],
                "negative": ["7", 0], "latent_image": ["5", 0]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "ugly, blurry, low quality, distorted, cartoon, anime, bright colors, happy, cheerful", "clip": ["4", 1]}
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

    data = json.dumps({"prompt": workflow}).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(req)
    result = json.loads(response.read())
    prompt_id = result['prompt_id']

    max_wait = 180
    waited = 0
    while waited < max_wait:
        req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
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
                    import shutil
                    shutil.copy2(str(src), str(dst))
                    return str(dst)
        await asyncio.sleep(2)
        waited += 2
    return None
def split_story(story: str):
    """Разделяет рассказ на 3 равные части"""
    paragraphs = [p.strip() for p in story.split('\n') if p.strip()]
    
    # Сначала пытаемся разделить по абзацам
    if len(paragraphs) >= 3:
        third = len(paragraphs) // 3
        
        # Находим границы для первой трети
        mid1 = third
        for i in range(mid1, len(paragraphs)):
            if paragraphs[i].strip().endswith(('.', '!', '?')):
                mid1 = i + 1
                break
        
        # Находим границы для второй трети
        mid2 = 2 * third
        for i in range(mid2, len(paragraphs)):
            if paragraphs[i].strip().endswith(('.', '!', '?')):
                mid2 = i + 1
                break
        
        part1 = '\n\n'.join(paragraphs[:mid1])
        part2 = '\n\n'.join(paragraphs[mid1:mid2])
        part3 = '\n\n'.join(paragraphs[mid2:])
    else:
        # Если мало абзацев, делим по предложениям
        sentences = story.split('. ')
        third = len(sentences) // 3
        
        mid1 = third
        for i in range(mid1, len(sentences)):
            if sentences[i].strip().endswith(('.', '!', '?')):
                mid1 = i + 1
                break
        
        mid2 = 2 * third
        for i in range(mid2, len(sentences)):
            if sentences[i].strip().endswith(('.', '!', '?')):
                mid2 = i + 1
                break
        
        part1 = '. '.join(sentences[:mid1])
        part2 = '. '.join(sentences[mid1:mid2])
        part3 = '. '.join(sentences[mid2:])
    
    # Проверяем баланс частей
    part1_words = len(part1.split())
    part2_words = len(part2.split())
    part3_words = len(part3.split())
    total_words = part1_words + part2_words + part3_words
    
    if total_words > 0:
        # Проверяем разницу между самой большой и самой маленькой частью
        max_words = max(part1_words, part2_words, part3_words)
        min_words = min(part1_words, part2_words, part3_words)
        ratio = (max_words - min_words) / max_words
        
        # Если разница больше 20%, делим по словам
        if ratio > 0.2:
            words = story.split()
            third_word = len(words) // 3
            
            # Находим первую границу
            mid1_word = third_word
            for i in range(mid1_word, len(words)):
                if words[i].endswith(('.', '!', '?')):
                    mid1_word = i + 1
                    break
            
            # Находим вторую границу
            mid2_word = 2 * third_word
            for i in range(mid2_word, len(words)):
                if words[i].endswith(('.', '!', '?')):
                    mid2_word = i + 1
                    break
            
            part1 = ' '.join(words[:mid1_word])
            part2 = ' '.join(words[mid1_word:mid2_word])
            part3 = ' '.join(words[mid2_word:])
    
    return part1, part2, part3


def create_cover(image_path: str, title: str, part_num: int, output_path: str):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    creepster_font = str(FONTS_DIR / "Creepster-Regular.ttf")
    
    title_font = ImageFont.truetype(TITLE_FONT_PATH, 90)
    part_font = ImageFont.truetype(creepster_font, 64)

    # Разбиваем название на две строки если больше одного слова
    title_words = title.upper().split()
    if len(title_words) > 1:
        mid = len(title_words) // 2
        title_lines = [" ".join(title_words[:mid]), " ".join(title_words[mid:])]
    else:
        title_lines = [title.upper()]

    # Вычисляем позицию для центрирования
    line_height = 100
    total_title_height = line_height * len(title_lines)
    title_y_start = (img.height // 2) - (total_title_height // 2) - 30

    # Рисуем каждую строку названия
    for i, line in enumerate(title_lines):
        line_bbox = draw.textbbox((0, 0), line, font=title_font)
        line_w = line_bbox[2] - line_bbox[0]
        line_x = (img.width - line_w) // 2
        line_y = title_y_start + i * line_height

        for dx in range(-5, 6):
            for dy in range(-5, 6):
                draw.text((line_x + dx, line_y + dy), line, font=title_font, fill="black")
        draw.text((line_x, line_y), line, font=title_font, fill=(220, 0, 0))

    part_text = f"Part {part_num}"
    part_bbox = draw.textbbox((0, 0), part_text, font=part_font)
    part_w = part_bbox[2] - part_bbox[0]
    part_x = (img.width - part_w) // 2
    part_y = title_y_start + total_title_height + 20

    for dx in range(-4, 5):
        for dy in range(-4, 5):
            draw.text((part_x + dx, part_y + dy), part_text, font=part_font, fill="black")
    draw.text((part_x, part_y), part_text, font=part_font, fill=(220, 0, 0))

    img.save(output_path)
    print(f"   Обложка сохранена: {output_path}")


def create_video(image_path: str, audio_path: str, output_path: str, effect: str):
    import random
    music_dir = Path("music")
    music_files = list(music_dir.glob("*.mp3"))
    music_file = str(random.choice(music_files)) if music_files else None

    effect_filters = {
        "vhs_glitch": (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "noise=alls=28:allf=t+u,"
            "eq=contrast=1.14:brightness=-0.06:saturation=1.34,"
            "hue=h=1.2*t:enable='between(mod(t\\,0.3)\\,0\\,0.03)'"
        ),
        "film_grain": (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "noise=alls=38:allf=t,"
            "eq=contrast=1.19:brightness=-0.04:saturation=0.88"
        ),
        "static_noise": (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "noise=alls=58:allf=t+u,"
            "eq=contrast=1.24:brightness=-0.09:saturation=0.66"
        ),
        "scan_lines": (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "eq=contrast=1.14:brightness=-0.06,"
            "noise=alls=10:allf=t"
        ),
        "datamosh": (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "noise=alls=23:allf=t,"
            "eq=contrast=1.14:brightness=-0.05:saturation=1.24"
        ),
    }

    vf_base = effect_filters.get(effect, effect_filters["film_grain"])
    zoompan = "zoompan=z='min(zoom+0.0015,1.5)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920"
    vf = f"{zoompan},{vf_base}"

    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
    ]

    if music_file:
        cmd.extend(["-stream_loop", "-1", "-i", music_file])
        cmd.extend([
            "-filter_complex",
            f"[1:a]volume=1.0[voice];[2:a]volume=0.4[music];[voice][music]amix=inputs=2:duration=first[aout]",
            "-map", "0:v",
            "-map", "[aout]",
        ])
    else:
        cmd.extend(["-map", "0:v", "-map", "1:a"])

    cmd.extend([
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "28",
        "-b:v", "1000k",
        "-maxrate", "1500k",
        "-bufsize", "2000k",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-r", "24",
        "-movflags", "+faststart",
        output_path
    ])

    subprocess.run(cmd, capture_output=True, check=True)
    music_name = Path(music_file).name if music_file else "нет"
    print(f"   Видео сохранено: {output_path} (эффект: {effect}, музыка: {music_name})")


def get_next_story_id():
    existing = [d for d in OUTPUT_DIR.iterdir() if d.is_dir() and d.name[:3].isdigit()]
    if not existing:
        return 1
    ids = [int(d.name[:3]) for d in existing]
    return max(ids) + 1


async def main():
    import sys
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        print("Генерация случайной темы...")
        topic = await generate_topic()
        print(f"Сгенерированная тема: {topic}\n")

    story_id = get_next_story_id()
    clean_topic = topic.replace("Тема:", "").replace("тема:", "").strip()
    clean_topic = clean_topic[:50]
    safe_topic = "".join(c if c.isalnum() or c in " _-" else "_" for c in clean_topic)
    safe_topic = "_".join(safe_topic.split())[:50]
    if not safe_topic:
        safe_topic = f"story_{story_id}"
    story_dir = OUTPUT_DIR / f"{story_id:03d}_{safe_topic}"
    story_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Генерация крипипасты #{story_id} ===")
    print(f"Тема: {topic}")
    print(f"Папка: {story_dir}\n")

    print("1. Параллельная генерация названия и хештегов...")
    title_task = generate_title(topic)
    hashtags_task = generate_hashtags(topic)
    title, hashtags = await asyncio.gather(title_task, hashtags_task)

    (story_dir / "title.txt").write_text(title, encoding="utf-8")
    print(f"   Название: {title}")
    
    hashtags_part1 = f"{title} #1 {hashtags}"
    hashtags_part2 = f"{title} #2 {hashtags}"
    hashtags_part3 = f"{title} #3 {hashtags}"
    
    (story_dir / "hashtags_part1.txt").write_text(hashtags_part1, encoding="utf-8")
    (story_dir / "hashtags_part2.txt").write_text(hashtags_part2, encoding="utf-8")
    (story_dir / "hashtags_part3.txt").write_text(hashtags_part3, encoding="utf-8")
    print(f"   Хештеги: {hashtags}\n")

    print("2. Генерация рассказа...")
    story = await generate_story(topic)
    (story_dir / "story.txt").write_text(story, encoding="utf-8")
    word_count = len(story.split())
    print(f"   Рассказ: {word_count} слов\n")

    print("3. Разделение на 3 части...")
    part1, part2, part3 = split_story(story)
    (story_dir / "story_part1.txt").write_text(part1, encoding="utf-8")
    (story_dir / "story_part2.txt").write_text(part2, encoding="utf-8")
    (story_dir / "story_part3.txt").write_text(part3, encoding="utf-8")
    print(f"   Часть 1: {len(part1.split())} слов")
    print(f"   Часть 2: {len(part2.split())} слов")
    print(f"   Часть 3: {len(part3.split())} слов\n")

    print("4. Параллельная генерация озвучки и промпта изображения...")
    voice1_path = str(story_dir / "voice_part1.mp3")
    voice2_path = str(story_dir / "voice_part2.mp3")
    voice3_path = str(story_dir / "voice_part3.mp3")
    voice1_task = generate_voice(part1, voice1_path)
    voice2_task = generate_voice(part2, voice2_path)
    voice3_task = generate_voice(part3, voice3_path)
    image_prompt_task = generate_image_prompt(story, topic)
    _, _, _, image_prompt = await asyncio.gather(voice1_task, voice2_task, voice3_task, image_prompt_task)
    (story_dir / "image_prompt.txt").write_text(image_prompt, encoding="utf-8")
    print(f"   Промпт: {image_prompt[:80]}...\n")

    print("5. Генерация изображения...")
    image_path = await generate_image(image_prompt, story_dir)
    print(f"   Изображение: {image_path}\n")

    print("6. Создание обложек...")
    cover1_path = str(story_dir / "cover_part1.png")
    cover2_path = str(story_dir / "cover_part2.png")
    cover3_path = str(story_dir / "cover_part3.png")
    create_cover(image_path, title, 1, cover1_path)
    create_cover(image_path, title, 2, cover2_path)
    create_cover(image_path, title, 3, cover3_path)
    print()

    print("7. Создание видео...")
    video1_path = str(story_dir / "video_part1.mp4")
    video2_path = str(story_dir / "video_part2.mp4")
    video3_path = str(story_dir / "video_part3.mp4")
    effect1 = random.choice(EFFECTS)
    effect2 = random.choice(EFFECTS)
    effect3 = random.choice(EFFECTS)
    create_video(image_path, voice1_path, video1_path, effect1)
    create_video(image_path, voice2_path, video2_path, effect2)
    create_video(image_path, voice3_path, video3_path, effect3)
    print()

    print("=== Готово! ===")
    print(f"Папка: {story_dir}")
    print(f"Файлы:")
    for f in sorted(story_dir.iterdir()):
        size = f.stat().st_size
        if size > 1024 * 1024:
            print(f"  {f.name:25s} {size / 1024 / 1024:.1f} MB")
        elif size > 1024:
            print(f"  {f.name:25s} {size / 1024:.1f} KB")
        else:
            print(f"  {f.name:25s} {size} B")


if __name__ == "__main__":
    asyncio.run(main())
