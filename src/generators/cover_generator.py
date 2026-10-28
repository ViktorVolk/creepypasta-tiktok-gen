from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ..config import TITLE_FONT_PATH, CREEPSTER_FONT_PATH


class CoverGenerator:
    def __init__(self):
        self.title_font_path = TITLE_FONT_PATH
        self.creepster_font_path = CREEPSTER_FONT_PATH

    def create(self, image_path: str, title: str, part_num: int, output_path: str) -> str:
        image_path = Path(image_path)
        output_path = Path(output_path)
        
        if not image_path.exists():
            raise ValueError(f"Изображение не найдено: {image_path}")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Название должно быть непустой строкой")
        if not isinstance(part_num, int) or part_num <= 0:
            raise ValueError("Номер части должен быть положительным целым числом")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        title_font = ImageFont.truetype(self.title_font_path, 72)
        part_font = ImageFont.truetype(str(self.creepster_font_path), 64)

        title_words = title.upper().split()
        if len(title_words) > 1:
            mid = len(title_words) // 2
            title_lines = [" ".join(title_words[:mid]), " ".join(title_words[mid:])]
        else:
            title_lines = [title.upper()]

        line_height = 80
        total_title_height = line_height * len(title_lines)
        title_y_start = (img.height // 2) - (total_title_height // 2) - 30

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

        img.save(str(output_path))
        return str(output_path)
