from pathlib import Path
from ..config import STORIES_DIR


class FileManager:
    def __init__(self):
        self.stories_dir = STORIES_DIR

    def get_next_story_id(self) -> int:
        self.stories_dir.mkdir(parents=True, exist_ok=True)
        existing = [d for d in self.stories_dir.iterdir() if d.is_dir() and d.name[:3].isdigit()]
        if not existing:
            return 1
        ids = [int(d.name[:3]) for d in existing]
        return max(ids) + 1

    def create_story_dir(self, story_id: int, topic: str) -> Path:
        clean_topic = topic.replace("Тема:", "").replace("тема:", "").strip()
        clean_topic = clean_topic[:50]
        safe_topic = "".join(c if c.isalnum() or c in " _-" else "_" for c in clean_topic)
        safe_topic = "_".join(safe_topic.split())[:50]
        if not safe_topic:
            safe_topic = f"story_{story_id}"
        
        story_dir = self.stories_dir / f"{story_id:03d}_{safe_topic}"
        story_dir.mkdir(parents=True, exist_ok=True)
        return story_dir

    def save_text_file(self, story_dir: Path, filename: str, content: str) -> Path:
        file_path = story_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def save_hashtags(self, story_dir: Path, title: str, hashtags: str) -> None:
        for i in range(1, 4):
            content = f"{title} #{i} {hashtags}"
            self.save_text_file(story_dir, f"hashtags_part{i}.txt", content)
