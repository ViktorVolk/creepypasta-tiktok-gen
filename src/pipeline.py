import asyncio
import random
import urllib.request
from pathlib import Path
from .generators.text_generator import TextGenerator
from .generators.voice_generator import VoiceGenerator
from .generators.image_generator import ImageGenerator
from .generators.video_generator import VideoGenerator
from .generators.cover_generator import CoverGenerator
from .utils.story_splitter import StorySplitter
from .utils.file_manager import FileManager
from .config import COMFYUI_URL


class CreepypastaPipeline:
    def __init__(self):
        self.text_gen = TextGenerator()
        self.voice_gen = VoiceGenerator()
        self.image_gen = ImageGenerator()
        self.video_gen = VideoGenerator()
        self.cover_gen = CoverGenerator()
        self.splitter = StorySplitter()
        self.file_mgr = FileManager()

    def _check_comfyui(self) -> bool:
        try:
            req = urllib.request.Request(f"{COMFYUI_URL}/system_stats")
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False

    async def run(self, topic: str = None) -> Path:
        if not self._check_comfyui():
            raise ConnectionError(
                "ComfyUI не запущен. Запустите: python ComfyUI\\main.py --listen"
            )
        if topic is None:
            print("Генерация случайной темы...")
            topic = self.text_gen.generate_topic()
        
        topic = topic.replace("Тема:", "").replace("тема:", "").strip()
        story_id = self.file_mgr.get_next_story_id()
        story_dir = self.file_mgr.create_story_dir(story_id, topic)

        print(f"=== Генерация крипипасты #{story_id} ===")
        print(f"Тема: {topic}")
        print(f"Папка: {story_dir}\n")

        print("1. Генерация названия и хештегов...")
        title = self.text_gen.generate_title(topic)
        hashtags = self.text_gen.generate_hashtags(topic)
        
        self.file_mgr.save_text_file(story_dir, "title.txt", title)
        self.file_mgr.save_hashtags(story_dir, title, hashtags)
        print(f"   Название: {title}")
        print(f"   Хештеги: {hashtags}\n")

        print("2. Генерация рассказа...")
        story = self.text_gen.generate_story(topic)
        self.file_mgr.save_text_file(story_dir, "story.txt", story)
        word_count = len(story.split())
        print(f"   Рассказ: {word_count} слов\n")

        print("3. Разделение на 3 части...")
        part1, part2, part3 = self.splitter.split(story)
        self.file_mgr.save_text_file(story_dir, "story_part1.txt", part1)
        self.file_mgr.save_text_file(story_dir, "story_part2.txt", part2)
        self.file_mgr.save_text_file(story_dir, "story_part3.txt", part3)
        print(f"   Часть 1: {len(part1.split())} слов")
        print(f"   Часть 2: {len(part2.split())} слов")
        print(f"   Часть 3: {len(part3.split())} слов\n")

        print("4. Генерация промпта изображения...")
        image_prompt = self.text_gen.generate_image_prompt(story, topic)
        self.file_mgr.save_text_file(story_dir, "image_prompt.txt", image_prompt)
        print(f"   Промпт: {image_prompt[:80]}...\n")

        print("5. Генерация изображения...")
        image_path = await self.image_gen.generate(image_prompt, story_dir)
        print(f"   Изображение: {image_path}\n")

        print("6. Генерация озвучки (последовательно)...")
        
        if not part1.strip() or not part2.strip() or not part3.strip():
            raise ValueError("Одна из частей рассказа пустая. Проверьте разделение текста.")
        
        voice1_path = str(story_dir / "voice_part1.mp3")
        voice2_path = str(story_dir / "voice_part2.mp3")
        voice3_path = str(story_dir / "voice_part3.mp3")
        
        await self.voice_gen.generate(part1, voice1_path)
        print("   Часть 1 озвучена")
        
        await asyncio.sleep(3)
        await self.voice_gen.generate(part2, voice2_path)
        print("   Часть 2 озвучена")
        
        await asyncio.sleep(3)
        await self.voice_gen.generate(part3, voice3_path)
        print("   Часть 3 озвучена\n")

        print("7. Создание обложек...")
        cover1_path = str(story_dir / "cover_part1.png")
        cover2_path = str(story_dir / "cover_part2.png")
        cover3_path = str(story_dir / "cover_part3.png")
        
        self.cover_gen.create(image_path, title, 1, cover1_path)
        self.cover_gen.create(image_path, title, 2, cover2_path)
        self.cover_gen.create(image_path, title, 3, cover3_path)
        print()

        print("8. Создание видео...")
        video1_path = str(story_dir / "video_part1.mp4")
        video2_path = str(story_dir / "video_part2.mp4")
        video3_path = str(story_dir / "video_part3.mp4")
        
        self.video_gen.create(image_path, voice1_path, video1_path)
        self.video_gen.create(image_path, voice2_path, video2_path)
        self.video_gen.create(image_path, voice3_path, video3_path)
        print()

        print("=== Готово! ===")
        print(f"Папка: {story_dir}")
        self._print_files(story_dir)
        
        return story_dir

    def _print_files(self, story_dir: Path):
        print("Файлы:")
        for f in sorted(story_dir.iterdir()):
            size = f.stat().st_size
            if size > 1024 * 1024:
                print(f"  {f.name:25s} {size / 1024 / 1024:.1f} MB")
            elif size > 1024:
                print(f"  {f.name:25s} {size / 1024:.1f} KB")
            else:
                print(f"  {f.name:25s} {size} B")
